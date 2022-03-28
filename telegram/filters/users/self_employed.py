from common.crud import self_employed
from .common import UserFilter


class IsSelfEmployed(UserFilter, crud=self_employed):
    pass
