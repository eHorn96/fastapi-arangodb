from datetime import UTC, datetime, timedelta
from typing import Annotated, Any, Optional

import arango.exceptions
from arango import ArangoClient, JWTAuthError, ServerConnectionError
from arango.database import StandardDatabase
from arango.job import AsyncJob, BatchJob
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTClaimsError
from passlib.context import CryptContext
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from v1.config.config import ALGORITHM, BASE_DB_URL, CORS_ALLOWED_ORIGIN, DOMAIN, JWTSECRET, \
	SECRET_KEY
from v1.models.models import User
from v1.shared.shared import get_sys_client, get_sys_db, logger, read_auth_cookie

oauth2_scheme = OAuth2PasswordBearer(
	tokenUrl="auth/login",
	description="Login for accessing the API using OAuth2. The token can be exchanged for "
				"a valid authToken cookie.", )


def set_auth_header(response: Response, auth_token: str) -> Response:
	"""

	@param response:
	@type response:
	@param auth_token:
	@type auth_token:
	@return:
	@rtype:
	"""
	response: Response
	response.init_headers(headers={"Authorization": f"bearer {auth_token}"})
	return response


async def set_auth_cookie(response: Response, auth_token: str) -> Response:
	"""
	:param response: The HTTP response object to set the authentication cookie on.
	:type response: Response
	:param auth_token: The authentication token to be set as a cookie.
	:type auth_token: str
	:return: The modified HTTP response object with the authentication cookie set.
	:rtype: Response
	"""
	response.set_cookie(
		key="authToken", value=auth_token, httponly=True, max_age=1800, expires=1800,
		samesite="lax", domain=CORS_ALLOWED_ORIGIN, path="/", secure=True, )
	return response


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
	"""
	:param data: Dictionary containing the data to be encoded in the JWT token.
	:type data: dict
	:param expires_delta: Optional timedelta object defining the token expiration time. If not
	provided, the default expiration time of 15 minutes will be used.
	:type expires_delta: Optional[timedelta]
	:return: Encoded JWT token as a string.
	:rtype: str
	"""
	logger.info("Copying data to encode")
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.now(UTC) + expires_delta
	else:
		# Default to 15 minutes if no duration is provided
		expire = datetime.now(UTC) + timedelta(minutes=15)
	to_encode.update({"exp": expire})
	logger.debug(to_encode)
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	logger.debug(encoded_jwt)
	return encoded_jwt


def verify_password(plain_password, hashed_password):
	"""
	:param plain_password: The plain text password to be verified.
	:type plain_password: str
	:param hashed_password: The hashed password to verify against.
	:type hashed_password: str
	:return: True if the plain text password matches the hashed password, False otherwise.
	:rtype: bool
	"""
	return pwd_context.verify(plain_password, hashed_password)


async def get_user(username: str, ) -> dict[str, Any] | AsyncJob[dict[str, Any]] | BatchJob[
	dict[str, Any]] | None:
	"""

	:param username: The username of the user to retrieve from the CortexUsers database.
	:type username: str
	:return: User information if the user is found, otherwise None.
	:rtype: UserInDB or None
	"""
	db = get_sys_db()

	if not db.has_user(username):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
	logger.info(db.user(username))
	return db.user(username)


async def authenticate_user(username: str, password: str) -> str:
	"""
	:param username: The username of the user attempting to authenticate
	:type username: str
	:param password: The plaintext password of the user attempting to authenticate
	:type password: str
	:return: The authenticated user's database record if authentication is successful, otherwise
	None
	:rtype: Optional[UserInDB]

	"""
	try:

		user_db = get_sys_client().db(username=username, password=password, auth_method="jwt")

	except JWTAuthError as error:
		logger.debug(error.__str__())
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
	logger.info("Initiated Login Flow.")
	logger.info(f"Username exists: {bool(username)}")
	logger.info(f"Connecting to database")
	logger.info("Success.")
	logger.info(f"{user_db.conn._token}")
	return user_db.conn._token


async def get_current_user(request: Request) -> User:
	"""
	Dependency to get the current user from the authToken cookie.
	"""
	auth_token = await read_auth_cookie(request)

	logger.info("Getting current User...")
	if auth_token is None:
		logger.error("No Auth Token found.")
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials",
			headers={"WWW-Authenticate": "Bearer"}, )
	logger.info(f"Auth Token found: {bool(auth_token)}")
	try:
		logger.debug(f"{auth_token}")
		logger.info("Decoding Auth Token.")
		payload = jwt.decode(auth_token, JWTSECRET, algorithms=[ALGORITHM])
		logger.info("Getting payload from Auth Token.")
		username: str = payload.get("preferred_username")
		logger.info(f"Username from payload: {bool(username)}")
		logger.info(f"Issuer is ArangoDB:{bool(payload.get('iss') == 'arangodb')}")
		if username is None:
			logger.info("Username not found.")
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid authentication credentials",
				headers={"WWW-Authenticate": "Bearer"}, )
		logger.info(f"Username found: {bool(username)}")
		logger.info("Connectiing to database.")
		logger.info("Checking if token is expired.")
		user = await get_user(username)
		if user is None:
			logger.info("User not found.")
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found",
				headers={"WWW-Authenticate": "Bearer"}, )
		logger.info(f"User found: {bool(user)}")
		logger.info("Auth finished. Returning User.")

		return User(**user)

	except JWTClaimsError as error:
		logger.debug(error)
		logger.error("JWT Error.")
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials",
			headers={"WWW-Authenticate": "Bearer"}, )
	except Exception as e:
		logger.error(e)
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail=e.__dict__)


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)] ):

	if not current_user:
		raise HTTPException(status_code=401, detail="No active user found.")
	return current_user


async def get_current_active_user_db(request: Request,
									 current_user: Annotated[
										 User, Depends(get_current_user)]) -> StandardDatabase:
	auth_token: str = await read_auth_cookie(request)
	logger.info(f"Fetching User Database for {current_user.username}")
	try:
		client = ArangoClient(hosts=BASE_DB_URL)
		logger.info("Connected to ArangoHost")
		db: StandardDatabase = client.db(name=current_user.username, user_token=auth_token)
		logger.info("Connected to User Database")
		return db
	except arango.ArangoClientError as error:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)
	except ServerConnectionError as error:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)
