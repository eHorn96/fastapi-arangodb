from typing import Annotated

from arango import ArangoClient
from arango.database import StandardDatabase
from fastapi import APIRouter
from fastapi.params import Depends
from starlette.requests import Request

from v1.auth.utils import get_current_active_user, get_current_active_user_db
from v1.models.models import User
from v1.objects.collections.collections import collections_router
from v1.objects.models import CollectionInfo
from v1.objects.nodes.layouts.layouts import layouts_router
from v1.objects.nodes.nodes import nodes_router
from v1.shared.shared import read_auth_cookie

objects_router = APIRouter(prefix="/objects", tags=["Objects"])

objects_router.include_router(layouts_router)
objects_router.include_router(collections_router)








@objects_router.get(
	"/collections/{collection_id}/info", description="Fetch information from a specific "
													 "collection")
async def fetch_collection(auth_cookie: Annotated[str, Depends(read_auth_cookie)],
						   collection_id: str,
						   current_user: Annotated[
							   User, Depends(get_current_active_user)]) -> CollectionInfo:
	client = ArangoClient(hosts="http://localhost:8529")
	db = client.db(name=current_user.username, user_token=auth_cookie)
	return CollectionInfo(**db.collection(collection_id).info())
