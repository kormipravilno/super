from gino import Gino

from db.config import config

db = Gino()


async def init_db():
    await db.set_bind(config.DATABASE_URL)
    await db.gino.create_all()


async def close_db():
    await db.pop_bind().close()
