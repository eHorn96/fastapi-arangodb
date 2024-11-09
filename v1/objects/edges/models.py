from typing import List

from pydantic import BaseModel

from v1.models.models import BaseEdge


class GraphEdgeData(BaseModel):
	key: str
	value: str | float | int | bool | None = None


class GraphEdge(BaseEdge):
	name: str
	data: List[GraphEdgeData]
