from typing import Annotated, List

from arango.database import StandardDatabase
from fastapi import APIRouter
from fastapi.params import Depends

from v1.auth.utils import get_current_active_user_db

graphs_router = APIRouter(prefix="/graphs", tags=["Graphs"])


@graphs_router.get("", description="Fetch all accessible graphs")
async def get_graphs(db: Annotated[StandardDatabase, Depends(get_current_active_user_db)]) -> List[
	dict]:
	return db.graphs()


@graphs_router.get("/{graph_id}", description="Fetch specified graphs properties.")
async def get_graph(graph_id: str,
					db: Annotated[StandardDatabase, Depends(get_current_active_user_db)]) -> dict:

	return db.graph(graph_id).properties()
