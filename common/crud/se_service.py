from models.users import SelfEmployedServiceModel
from common.schemas import SEServiceGet, SEServiceSchema
from .base import CRUDBase


class SEServiceCRUD(CRUDBase[SelfEmployedServiceModel, SEServiceGet, SEServiceSchema]):
    pass


se_service = SEServiceCRUD(SelfEmployedServiceModel, SEServiceGet, SEServiceSchema)
