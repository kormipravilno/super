from common.crud import admin
from .common import UserFilter


class IsAdmin(UserFilter, crud=admin):
    pass
