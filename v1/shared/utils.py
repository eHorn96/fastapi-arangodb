from typing import Annotated

from arango.database import StandardDatabase
from arango.graph import Graph
from fastapi.params import Depends

from v1.auth.utils import get_current_active_user_db


async def fetch_user_graph(db: Annotated[
	StandardDatabase, Depends(get_current_active_user_db)]) -> Graph:
	raise NotImplementedError
