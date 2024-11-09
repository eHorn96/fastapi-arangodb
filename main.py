import os
from contextlib import asynccontextmanager
from typing import Sequence

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
	load_dotenv('.devenv')
	BASE_URL = os.environ.get('BASE_URL')
	print(BASE_URL)

	yield
	print("Bye!")


app = FastAPI(lifespan=lifecycle)

app.include_router(router)

origins: Sequence[str] = (
	f"https://{CORS_ALLOWED_ORIGIN}/login", f"https://{CORS_ALLOWED_ORIGIN}/token",
	f"https://{CORS_ALLOWED_ORIGIN}",f"https://{CORS_ALLOWED_ORIGIN}/register")
logger.info("Adding CORS Middleware")
cors = CORSMiddleware(
	app, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
print(cors.__dict__)

app.add_middleware(
	middleware_class=CORSMiddleware, allow_origins=origins, allow_credentials=True,
	allow_methods=["*"], allow_headers=["*"])


@app.get("/")
async def root():
	return "works"


@app.get("/hello/{name}")
async def say_hello(name: str):
	return {"message": f"Hello {name}"}
