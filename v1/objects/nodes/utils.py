from typing import Annotated, List

from arango.database import StandardDatabase
from fastapi.params import Depends

from v1.auth.utils import get_current_active_user
from v1.models.models import User
from v1.shared.shared import get_sys_db


async def get_user_accessible_dbs(current_user: Annotated[User, Depends(get_current_active_user)]):
	db: StandardDatabase = get_sys_db()
	# TODO: Implement later
