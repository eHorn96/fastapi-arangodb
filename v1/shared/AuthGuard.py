from typing import Optional

from arango import ArangoClient
from arango.database import StandardDatabase
from passlib.context import CryptContext

from v1.config.config import ARANGO_ROOT_PW


class AuthGuard:
	def __init__(self,
				 db_name: Optional[str] = "_system",
				 username: Optional[str] = "root",
				 password: Optional[str] = ARANGO_ROOT_PW,
				 auth_token: Optional[str] = None):
		self.db_name = db_name
		self.username = username
		self.password = password
		self.auth_token = auth_token
		from fastapi.security import OAuth2PasswordBearer
		self.oauth2_scheme = OAuth2PasswordBearer(
			tokenUrl="/token",
			description="Login for accessing the APIusing Oauth2. The token can be exchanged for "
						"a "
						"valid auth_token cookie.")
		self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

		# Init Db connection. Fail if it doesn't work.
		self._init_db()

	def __call__(self, ):
		pass

	def verify_password(self, plain_password: str, hashed_password):
		"""
		:param plain_password: The plain text password to be verified.
		:type plain_password: str
		:param hashed_password: The hashed password to verify against.
		:type hashed_password: str
		:return: True if the plain text password matches the hashed password, False otherwise.
		:rtype: bool
		"""
		return self.pwd_context.verify(plain_password, hashed_password)

	def _init_db(self):
		# Not catching, exceptions should propagate from arango and be catched higher up.
		self.db: StandardDatabase = ArangoClient(hosts="http://localhost:8529").db(
			name=self.db_name, username=self.username, password=self.password, auth_method="jwt")

	async def authenticate_basic(self):
		if not self.username or not self.password:
			raise IOError("Username and password are required.")
