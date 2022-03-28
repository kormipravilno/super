from common.crud import courier

from ..group import USERS

COURIER = USERS.group("courier", courier)
