from typing import Annotated, Any, Dict, List

from arango.database import StandardDatabase
from fastapi import APIRouter, Depends
from fastapi.requests import Request

from v1.auth.utils import get_current_active_user_db
from v1.objects.nodes.nodes import nodes_router

collections_router = APIRouter(prefix="/collections", tags=["Collections"])

collections_router.include_router(nodes_router)


@collections_router.get(
	"", description="Fetch all accessible collections from the database")
async def get_metadata(request: Request,
					   db: Annotated[StandardDatabase, Depends(get_current_active_user_db)]):

	return db.collections()


@collections_router.get(
	"/{collection_id}", description="Fetch all documents from a specific collection")
async def fetch_all_docs(collection_id: str,
						 db: Annotated[StandardDatabase, Depends(get_current_active_user_db)]) -> \
		List[Dict[str, Any]]:
	return [doc for doc in db.collection(collection_id).all()]
