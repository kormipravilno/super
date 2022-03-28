from common.crud import self_employed

from ..group import USERS

SELF_EMPLOYED = USERS.group("self_employed", self_employed)
