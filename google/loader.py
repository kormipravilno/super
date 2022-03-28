import asyncio

loop = asyncio.new_event_loop()

from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from google.config import config

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

client = Aiogoogle(
    service_account_creds=ServiceAccountCreds(scopes=SCOPES, **config.GOOGLE)
)
