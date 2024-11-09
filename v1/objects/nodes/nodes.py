from typing import Annotated

from arango.database import StandardDatabase
from fastapi import APIRouter, Body, Depends

from v1.auth.utils import get_current_active_user, get_current_active_user_db
from v1.models.models import User
from v1.objects.nodes.models import GraphNode

nodes_router = APIRouter(prefix="/nodes", tags=["Nodes"])


@nodes_router.post("/",status_code=201)
async def post_node(db: Annotated[StandardDatabase,Depends(get_current_active_user_db)],
					node: GraphNode):
	return db.collection(node.collection).insert(node.dict())


@nodes_router.get("/{node_key}",response_model=GraphNode)
async def get_nodes(org_key: str,
					key: str,
					current_user: Annotated[User, Depends(get_current_active_user)]):
	pass
