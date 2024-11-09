import logging
from typing import Annotated

from arango import ArangoClient
from arango.database import StandardDatabase
from fastapi import HTTPException, Request
from fastapi.params import Depends
from starlette import status

from v1.config.config import ARANGO_ROOT_PW, BASE_DB_URL
from v1.models.models import User


def get_sys_client() -> ArangoClient:
	"""
	Functin to return a standard ArangoClient instance on which a user can be logged in on.
	@return:
	@rtype:
	"""
	return ArangoClient(hosts=BASE_DB_URL)


def get_sys_db() -> StandardDatabase:
	"""
	Function to return a connection to the _system database, which is used for managing the
	ArangoDB
	instance or cluster.
	@return:
	@rtype:
	"""

	client: ArangoClient = get_sys_client()
	db: StandardDatabase = client.db(username="root", password=ARANGO_ROOT_PW, auth_method="jwt")
	return db


async def get_current_user_db(request: Request, ):
	"""
	Dependency used for connecting a user to the main database.
	TODO: Implement Access-control for multi-tenancy.
	@param request:
	@type request:
	@return:
	@rtype:
	"""
	auth_token: str = await read_auth_cookie(request)
	logger.info(f"AuthToken set:  {auth_token is not None}")
	if not auth_token:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to authenticate")
	logger.info(f"AuthToken set: {auth_token is not None}")
	return get_sys_client().db("main", user_token=auth_token)


logger = logging.getLogger("cortex_backend")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter(
	"%(filename)s:%(lineno)s - %(funcName)s -  %(levelname)s - %(message)s")
ch.setFormatter(formatter)

logger.addHandler(ch)


async def read_auth_cookie(request: Request) -> str | None:
	"""
	Dependency for retrieving the cookie-header from the request. Gain Access to the request
	by adding `request:Request` to the particular function signature and call in the
	logic, or directly execute the dependency. Dependencies called in the latter way automatically
	pass the request to the function.

	:param request: The incoming HTTP request containing potential cookies.
		It doesn't have to be set, it gets passed automatically, if called through a
		decorated endpoint.
	:type request: Request
	:return: The authorization token if present in the cookies, otherwise None.
	:rtype: str | None.
	"""
	logger.info("Fetching Auth Cookie")
	auth_token = request.cookies.get("authToken")
	if auth_token:
		logger.info("Auth Token found in cookies.")
		return auth_token
	logger.info("Auth Token not found in cookies.")
	return None


async def get_available_databases(request: Request, current_user: Annotated[User, Depends()]):
	"""
	Guard function to check whether the database is accessible to the user trying to access it.
	@param request: The request object. Passed to function automatically if declared inside a
		FastAPI Dependency inside a function signature.
	@type request: Request
	@return: Dict[str,Any]
	"""
	raise NotImplementedError
