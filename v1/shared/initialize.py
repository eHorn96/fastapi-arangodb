from arango.database import StandardDatabase
from starlette import status
from starlette.exceptions import HTTPException

from v1.config.config import ARANGO_ROOT_PW, BASE_DB_URL, BASE_URL
from v1.models.models import User
from v1.shared.shared import get_sys_client, get_sys_db, logger

core_databases = ["main"]

core_doc_colls = ["Customers", "Suppliers", "Products", "Modules", "RawMaterials", "Roles", "Users",
				  "Teams", "Departments", "Events", "Objects", "Tasks", "Activities",
				  "SalesOrders",
				  "Organizations"
				  "PurchaseOrders", "WorkOrders", "StockAreas", "Services"]
core_edge_colls = ["EDGES", "MODULE_ASSEMBLES_INTO", "SUPPLIER_OFFERS", "CUSTOMER_BUYS",
				   "USER_BUYS", "DEPARTMENT_HAS", "ORGANIZATION_HAS", "USER_IS", "USER_LEADS",
				   "EVENT_TRIGGERS", "ACTIVITY_IS_PART_OF", "CUSTOMER_PLACES", "USER_PLACES",
				   "STOCKAREA_CONTAINS", "USER_DOES"]

CORE_GRAPH = [{
	"edge_collection"      : "EDGES", "from_vertex_collections": ["Objects"],
	"to_vertex_collections": ["Objects"]
}, {
	"edge_collection"      : "MODULE_ASSEMBLES_INTO", "from_vertex_collections": ["Modules"],
	"to_vertex_collections": ["Products"]
}, {
	"edge_collection"      : "SUPPLIER_OFFERS", "from_vertex_collections": ["Suppliers"],
	"to_vertex_collections": ["RawMaterials", "Modules", "Products", "Services", "Objects"]
}, {
	"edge_collection"      : "CUSTOMER_BUYS", "from_vertex_collections": ["Customers"],
	"to_vertex_collections": ["RawMaterials", "Modules", "Products", "Services", "Objects"]
}, {
	"edge_collection"      : "USER_BUYS", "from_vertex_collections": ["Users"],
	"to_vertex_collections": ["Products"]
}, {
	"edge_collection"      : "ORGANIZATION_HAS", "from_vertex_collections": ["Organizations"],
	"to_vertex_collections": ["Departments"]
}, {
	"edge_collection"      : "DEPARTMENT_HAS", "from_vertex_collections": ["Departments"],
	"to_vertex_collections": ["Users", "Teams"]
}, {
	"edge_collection"      : "USER_IS", "from_vertex_collections": ["Users"],
	"to_vertex_collections": ["Customers", "Suppliers"]
}, {
	"edge_collection"      : "USER_LEADS", "from_vertex_collections": ["Users"],
	"to_vertex_collections": ["Teams", "Departments", "Users"]
}, {
	"edge_collection"      : "EVENT_TRIGGERS", "from_vertex_collections": ["Events"],
	"to_vertex_collections": ["Tasks", "Activities", "Users"]
}, {
	"edge_collection"      : "ACTIVITY_IS_PART_OF", "from_vertex_collections": ["Activities"],
	"to_vertex_collections": ["Products", "Modules", "Services"]
}, {
	"edge_collection"      : "CUSTOMER_PLACES", "from_vertex_collections": ["Customers"],
	"to_vertex_collections": ["SalesOrders"]
}, {
	"edge_collection"      : "USER_PLACES", "from_vertex_collections": ["Users"],
	"to_vertex_collections": ["PurchaseOrders"]
}, {
	"edge_collection"      : "STOCKAREA_CONTAINS", "from_vertex_collections": ["StockAreas"],
	"to_vertex_collections": ["Products", "Modules", "RawMaterials"]
}, ]


def initialize_application(db_name: str = "main") -> None:
	"""
	Init-function for creating the user-space database and collections required for the application
	@return: None
	@rtype:
	"""
	logger.info(f"Configured DB Host for Cross Origins: {BASE_DB_URL}")
	logger.info(f"Configured Backend Host Cross-Origins: {BASE_URL}")
	client = get_sys_client()
	db = get_sys_db()
	if not db.has_database(db_name):
		db.create_database(db_name)
		logger.info(f"Created database {db_name}")
	main_database = client.db(db_name, username="root", password=ARANGO_ROOT_PW, auth_method="jwt")

	registered_users = db.users()

	for user in registered_users:
		logger.info(f"Updating user database {user['username']}")
		if user["username"] == "root":
			continue
		logger.info(f"{user['username']} is registered")
		if not db.has_database(user['username']):
			db.create_database(user['username'])
		db.update_permission(user['username'], "rw", user['username'])
		user_db = client.db(name=user["username"], username="root", password=ARANGO_ROOT_PW)

		if not user_db.has_graph("MainGraph"):
			user_db.create_graph("MainGraph", edge_definitions=CORE_GRAPH)

		for coll in core_doc_colls:
			if not user_db.has_collection(coll):
				user_db.create_collection(coll)
				logger.info(f"Created Document collection {coll}")
		for e_coll in core_edge_colls:
			if not user_db.has_collection(e_coll):
				user_db.create_collection(e_coll, edge=True)
				logger.info(f"Created Edge collection {e_coll} in database {db_name}")

	for node_col in core_doc_colls:

		if not main_database.has_collection(node_col):
			main_database.create_collection(node_col)
			logger.info(f"Created {node_col} collection")
	for edge_col in core_edge_colls:
		if not main_database.has_collection(edge_col):
			main_database.create_collection(edge_col, edge=True)
			logger.info(f"Created {edge_col} collection")


def create_org_db(user: User, db_name: str):
	db: StandardDatabase = get_sys_db()
	if not db.has_database(db_name):
		return db.create_database(db_name, users=[{user.username: "rw"}])
	else:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT, detail="Database already exists")
