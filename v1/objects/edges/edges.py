from fastapi import APIRouter

edges_router = APIRouter(prefix="/edges", tags=["Edges"])


@edges_router.get(
	'/', description='Fetch metadata about the Relationship collections accessible to you')
async def get_edges():
	pass
