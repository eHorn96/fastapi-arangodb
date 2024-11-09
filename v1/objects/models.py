from dataclasses import Field

from pydantic import BaseModel


class CollectionInfo(BaseModel):
	id: str
	name: str
	system: bool
	type: int
	edge: bool
	status: int
	global_id: str
