from datetime import date
from typing import Any, Dict, List

from nanoid import generate
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Address(BaseModel):
	model_config = ConfigDict(extra="allow")
	name: str
	street: str
	house_number: int | str | None = Field(None, alias = "houseNumber")
	city: str | None = Field(None)
	zip_code: str | None = Field(None)




class UserExtra(BaseModel):
	email: EmailStr | None = None
	full_name: str | None = Field(None, alias="fullName")
	address: Address | None = None
	birthday: date | None = None
	organisations: List[str] |None = Field(None)


class User(BaseModel):
	username: str | None = None
	is_active: bool = True
	is_superuser: bool = False
	extra: UserExtra


class UserRegister(User):
	password: str


class UserToken(BaseModel):
	token: str
	user_data: UserRegister | None = None


class UserLogin(BaseModel):
	username: str | None = None
	password: str | None = None


class CenterConfig(BaseModel):
	x: float = Field(0.5, description="Center X-coordinate")
	y: float = Field(0.5, description="Center Y-coordinate")


class ChargeConfig(BaseModel):
	enabled: bool = Field(True, description="Enable or disable charge force")
	strength: float = Field(-30, description="Strength of the charge force")
	distanceMin: float = Field(1, description="Minimum distance for charge force")
	distanceMax: float = Field(2000, description="Maximum distance for charge force")


class CollideConfig(BaseModel):
	enabled: bool = Field(True, description="Enable or disable collision detection")
	strength: float = Field(0.7, description="Strength of the collision detection")
	radius: float = Field(5, description="Radius of the nodes for collision detection")
	iterations: int = Field(1, description="Number of iterations for collision detection")


class ForceXConfig(BaseModel):
	enabled: bool = Field(False, description="Enable or disable force in X direction")
	strength: float = Field(0.1, description="Strength of the force in X direction")
	x: float = Field(0.5, description="X-coordinate to which the force pulls the nodes")


class ForceYConfig(BaseModel):
	enabled: bool = Field(False, description="Enable or disable force in Y direction")
	strength: float = Field(0.1, description="Strength of the force in Y direction")
	y: float = Field(0.5, description="Y-coordinate to which the force pulls the nodes")


class LinkConfig(BaseModel):
	enabled: bool = Field(True, description="Enable or disable link force")
	distance: float = Field(30, description="Desired distance between linked nodes")
	iterations: int = Field(1, description="Number of iterations for link adjustments")


class GraphConfig(BaseModel):
	center: CenterConfig = Field(
		default_factory=CenterConfig, description="Configuration for graph centering")
	charge: ChargeConfig = Field(
		default_factory=ChargeConfig, description="Configuration for charge force")
	collide: CollideConfig = Field(
		default_factory=CollideConfig, description="Configuration for collision detection", )
	forceX: ForceXConfig = Field(
		default_factory=ForceXConfig, description="Configuration for force in X direction", )
	forceY: ForceYConfig = Field(
		default_factory=ForceYConfig, description="Configuration for force in Y direction", )
	link: LinkConfig = Field(default_factory=LinkConfig, description="Configuration for link "
																	 "force")


class UserInDB(User):
	hashed_password: str


class UserCreate(User):
	model_config = ConfigDict(extra="allow")
	password: str


class UserGet(User):
	graphConfig: Dict[str, Any] | None = None


class BaseObject(BaseModel):

	key: str = Field(generate(), description="Unique Key.", alias="_key")
	name: str = Field(generate(), description="Unique Name. Defaults to random NANOID.")
	collection: str = Field("Objects", description="Collection name")


class BaseEdge(BaseObject):
	source: str = Field(..., description="Source Node", alias="_from")
	target: str = Field(..., description="Destination Node", alias="_to")
	collection: str = Field("Edges", description="Collection name")

class UserACL(BaseObject, User):
	collection: str = "Users"
