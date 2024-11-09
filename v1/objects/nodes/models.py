from typing import List

from pydantic import BaseModel

from v1.models.models import BaseObject


class GraphNodeData(BaseModel):
	key: str
	value: bool | int | float | str | None = None


class GraphNode(BaseObject):
	id: str
	name: str
	group: str
	data: List[GraphNodeData]
