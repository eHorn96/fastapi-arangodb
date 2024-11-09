import os
from typing import Literal

# Override with DEV ENV Variables if


API_RUN_MODE: Literal["DEV", "PROD"] = os.environ.get(
	"API_RUN_MODE", "DEV")  # Defaults to DEV just to be safe

DEV_DOMAIN: str = os.environ.get("DEV_DOMAIN", "localhost")
DEV_BASE_URL: str = os.environ.get("DEV_BASE_URL", "http://0.0.0.0:8080")
# the circusdb domain is for the Docker stack.
DEV_BASE_DB_URL: str = os.environ.get("DEV_BASE_DB_URL", "http://circusdb:8529")

# DO NOT EDIT
BASE_URL: str = os.environ.get("BASE_URL", DEV_BASE_URL)
BASE_DB_URL: str = os.environ.get("BASE_DB_URL", DEV_BASE_DB_URL)
#
PROD_BASE_URL: str = os.environ.get("PROD_BASE_URL", "https://0.0.0.0:8080")
PROD_BASE_DB_URL: str = os.environ.get("PROD_BASE_DB_URL", "http://circusdb:8529")

PYTHONPATH = "./"
JWTSECRET = os.environ.get("JWTSECRET")
SECRET_KEY = os.environ.get("SECRET_KEY")

ALGORITHM = os.environ.get("ALGORITHM", "HS256")  # Also defaults to HS256 to act as safeguard.
# A" Week == 60*24*7"
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")
ARANGO_ROOT_PW = os.environ.get("ARANGO_ROOT_PW", None)  # Should run into error
CORS_ALLOWED_ORIGIN = os.environ.get("CORS_ALLOWED_ORIGIN", None)
DOMAIN = BASE_URL.split('://')[-1]
