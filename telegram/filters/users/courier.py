from common.crud import courier
from .common import UserFilter


class IsCourier(UserFilter, crud=courier):
    pass
