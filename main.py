from contextlib import asynccontextmanager
from typing import Sequence

from dotenv import load_dotenv

load_dotenv('.env')
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.responses import HTMLResponse

from v1.config.config import CORS_ALLOWED_ORIGIN
from v1.routes import router
from v1.shared.initialize import initialize_application
from v1.shared.shared import logger


@asynccontextmanager
async def lifecycle(app: FastAPI):
	"""
	Lifecycle function which runs on start-up until the yield command and executes the logic
	after yield for custom teardown logic on shutdown.
	@param app:
	@type app:
	@return:
	@rtype:
	"""
	logger.info("Entering lifecycle")

	initialize_application()

	yield
	logger.info("Application stopped.")


app = FastAPI(lifespan=lifecycle)

app.include_router(router)

origins: Sequence[str] = (
	f"https://{CORS_ALLOWED_ORIGIN}/login", f"https://{CORS_ALLOWED_ORIGIN}/token",
	f"https://{CORS_ALLOWED_ORIGIN}",f"https://{CORS_ALLOWED_ORIGIN}/register")
logger.info("Adding CORS Middleware")
cors = CORSMiddleware(
	app, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.add_middleware(
	middleware_class=CORSMiddleware, allow_origins=origins, allow_credentials=True,
	allow_methods=["*"], allow_headers=["*"])


@app.get("/")
async def root():

	return HTMLResponse(
		status_code=status.HTTP_410_GONE, content="<h1>Root not callable.</h1>"

	)
