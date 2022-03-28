from models.users import CourierModel
from common.schemas import CourierSchema
from .base import CRUDBase


class CourierCRUD(CRUDBase[CourierModel, CourierSchema, CourierSchema]):
    pass


courier = CourierCRUD(CourierModel, CourierSchema)
