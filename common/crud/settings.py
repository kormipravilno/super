from models.settings import SettingsModel
from common.schemas import SettingsSchema
from .base import CRUDBase

# TODO correct type annotations
class SettingsCRUD(CRUDBase[SettingsModel, SettingsSchema, SettingsSchema]):
    def _return(self, db_obj: SettingsModel) -> str:
        return db_obj.value


settings = SettingsCRUD(SettingsModel, SettingsSchema, pk_col=SettingsModel.key)
