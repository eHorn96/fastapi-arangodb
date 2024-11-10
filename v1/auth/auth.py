"""
Dieses Modul definiert Authentifizierung-Routen für die FastAPI-Anwendung.

Es enthält Endpunkte für:
- Login (`/login`): Authentifiziert einen Benutzer und setzt ein HTTPOnly-Cookie
 mit dem Access-Token.
- Logout (`/logout`): Löscht das Authentifizierung-Cookie.

- Registrierung (`/register`): Registriert einen neuen Benutzer und erstellt
entsprechende Datenbank-Sammlungen und -Graphen.
- Token-Überprüfung (`/token`): Überprüft das aktuelle Authentifizierung-Cookie
und gibt Benutzerinformationen zurück.

Verwendete Bibliotheken und Module:
- datetime: Für die Berechnung des Token-Ablaufs.
- fastapi: Für die Erstellung der API-Router und Endpunkte.
- backend.api.v1.auth.utils: Enthält Hilfsfunktionen zur Benutzerauthentifizierung
 und Token-Erstellung.
- backend.api.v1.crud.dependencies: Beinhaltet Abhängigkeiten für die
 Datenbankverbindungen und das Logging.
- backend.api.v1.models. User: Definiert die Benutzer-Modelle
 für die Registrierung.

Konstanten:
- SECRET_KEY: Der geheime Schlüssel für die JWT-Token-Erstellung.
- ALGORITHM: Der Algorithmus zur JWT-Token-Erstellung.
- ACCESS_TOKEN_EXPIRE_MINUTES: Die Gültigkeitsdauer des Access-Tokens in Minuten.

API-Router:
- auth_router: Der Router für Authentifizierung-Endpunkte mit dem Präfix `/auth`.
"""

from typing import Annotated, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, Response
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request

from v1.config.config import ARANGO_ROOT_PW, CORS_ALLOWED_ORIGIN, DOMAIN
from v1.models.models import UserRegister
from .utils import (authenticate_user, get_current_active_user)
from ..shared.initialize import initialize_application
from ..shared.shared import get_sys_client, logger

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/login")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
	"""
	:param form_data: The form data containing the login credentials,
	 which includes `username` and `password`.
	:return: A Response object with status code 200 and an HTTPOnly
	 cookie containing the access token if authentication is successful;
	  raises an HTTPException with a 401 status code if authentication fails.
	"""

	# logger.info("Form Data contains Username: %s", bool(form_data.username))
	# logger.info("Form Data contains Password: %s", bool(form_data.password))
	user_token: str = await authenticate_user(form_data.username, form_data.password)
	if not user_token:
		logger.error("User not found.")
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"}, )

	logger.info("User authenticated")
	logger.info("Setting access token")
	# Set the authToken cookie
	logger.info("Set Response message")

	response.set_cookie(
		key="authToken", value=user_token, path="/", samesite="none", httponly=True, secure=True,
		domain=CORS_ALLOWED_ORIGIN)

	return {"message": "Logged in successfully"}


class LogoutResponse(Response):
	message: Dict[str, str] = {
		"message": "Successfully logged out",
	}


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request, response: Response):
	"""
	:param response: FastAPI Response object used to delete the authentication cookie.
	:return: A dictionary containing a success message indicating the user has been logged out.
	"""
	logger.info("Logging out user")
	response.delete_cookie(key="authToken", path='/', domain=DOMAIN)
	response.status_code = status.HTTP_200_OK
	return response


@auth_router.post("/register")
async def register(user: Annotated[UserRegister, Body()]):
	"""
	:param user: UserCreate object containing the user's registration information such as username,
	 password, full name, and email.
	:type user: Annotated[UserCreate, Body()]
	:return: A confirmation message indicating successful user registration.
	:rtype: dict
	"""
	logger.info("Connecting to System Database")
	client = get_sys_client()
	sys_db = client.db(username="root", password=ARANGO_ROOT_PW)
	logger.info("Checking for existing Username")
	if sys_db.has_user(user.username):
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT, detail="Username is already taken")
	logger.info("Creating new User")
	sys_db.create_user(
		user.username, user.password, extra=dict(
			email=user.extra.email, full_name=user.extra.full_name,

		))
	logger.info("Checking if database already exists")
	if sys_db.has_database(user.username):
		logger.info("User tried signing up with already existing username")
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT, detail="Username already registered", )
	logger.info("Initializing Database")
	initialize_application(user.username)
	logger.info("Adding User to newly created Database")
	sys_db.update_permission(user.username, "rw", user.username)
	user_graph = "Maingraph"

	logger.info("Connecting to User Database")
	arango_db_conn = client.db(
		name=f"{user.username}", username=user.username, password=user.password)
	logger.info("Connected to User's Database")

	return {
		"message": "User registered successfully", "status": arango_db_conn.context
	}


@auth_router.get("/token")
async def check_session_cookie(user: Annotated[dict | str, Depends(get_current_active_user)], ):
	"""
	:return: A dictionary containing the authentication status
	and the authenticated user's details such as username,
	 full name, and additional properties
	"""

	logger.info("Started Auth PW Flow.")

	logger.info(
		"Authenticated User: %s", bool(user), )
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication "
															 "credentials", )
	return {"message": "OK"}
