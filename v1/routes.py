from fastapi import  APIRouter

from v1.auth.auth import auth_router
from v1.graphs.graphs import graphs_router
from v1.objects.objects import objects_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(objects_router)
router.include_router(graphs_router)
