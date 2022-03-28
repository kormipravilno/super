import json
from logging import getLogger
from pprint import pprint
from typing import Any, Generic, Optional, Type, TypeVar
from pydantic import BaseModel

from db.engine import db

logger = getLogger(__name__)


ModelType = TypeVar("ModelType", bound=db.Model)
GetSchemaType = TypeVar("GetSchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class Relationship:
    def __init__(self, child: Type[ModelType], setter) -> None:
        """"""
        self.child = child
        self.setter = setter


class CRUDBase(Generic[ModelType, GetSchemaType, CreateSchemaType]):
    def __init__(
        self,
        model: Type[ModelType],
        get_schema: Type[GetSchemaType],
        create_schema: Type[CreateSchemaType] = None,
        *relationships: Relationship,
        pk_col: db.Column = None,
    ) -> None:
        """
        CRUD object with default methods for Create and Retrieve (CR__),
        since there is no need to Update or Delete

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class for retrieving
        * `relationships`: Relationships objects for loading
        """
        self.model = model
        self.get_schema = get_schema
        if create_schema:
            self.create_schema = create_schema
        else:
            self.create_schema = get_schema
        self.relationships = relationships

        if pk_col is not None:
            self.pk_col = pk_col
        else:
            self.pk_col = model.id

    async def __get(self, pk_val: Optional[Any] = None) -> list[ModelType]:
        query = self.model.query
        if pk_val is not None:
            query.append_whereclause(self.pk_col == pk_val)

        relationships = {}
        for relationship in self.relationships:
            query.append_from(self.model.outerjoin(relationship.child))
            query.append_column(relationship.child)
            relationships |= {relationship.setter: relationship.child}

        return await query.gino.load(
            self.model.distinct(self.pk_col).load(**relationships)
        ).all()

    def _return(self, db_obj) -> GetSchemaType:
        return self.get_schema.from_orm(db_obj)

    async def get(self, pk_val: ...):
        result = await self.__get(pk_val)
        if result:
            db_obj = result[0]
            return self._return(db_obj)

    async def get_all(self) -> list[GetSchemaType]:
        result = await self.__get()
        return [self._return(db_obj) for db_obj in result]

    async def raw_create_all(self, data: list[dict[str, Any]]) -> None:
        objs = [self.create_schema(**row) for row in data]
        return await self.create_all(objs)

    async def create_all(self, objs: list[CreateSchemaType]) -> None:
        logger.info(f"Creating data for [{self.model}] model...")
        objs_list = []
        for obj in objs:
            objs_list.append(json.loads(obj.json()))
        if objs_list:
            await self.model.insert().gino.all(objs_list)
        logger.info("Data created.")

    def __hash__(self) -> int:
        return hash(self.model.__tablename__)


async def purge():
    logger.info("Purging data...")
    for table in reversed(db.sorted_tables):
        logger.info(f"Purging {table}")
        await table.delete().gino.status()
    logger.info("Purged data.")
