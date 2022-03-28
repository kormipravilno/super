from models.users import AdminModel
from common.schemas import AdminSchema
from .base import CRUDBase


class AdminCRUD(CRUDBase[AdminModel, AdminSchema, AdminSchema]):
    pass


admin = AdminCRUD(AdminModel, AdminSchema)
