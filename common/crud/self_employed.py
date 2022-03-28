from models.users import SelfEmployedModel, SelfEmployedServiceModel
from common.schemas import SelfEmployedSchema, SelfEmployedGet
from .base import Relationship, CRUDBase


class SelfEmployedCRUD(
    CRUDBase[SelfEmployedModel, SelfEmployedGet, SelfEmployedSchema]
):
    pass


self_employed = SelfEmployedCRUD(
    SelfEmployedModel,
    SelfEmployedGet,
    SelfEmployedSchema,
    Relationship(SelfEmployedServiceModel, "add_service"),
)
