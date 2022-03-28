import pickle
import codecs
from typing import Callable, ClassVar
from pydantic import BaseModel


class InternalBase(BaseModel):
    key: ClassVar[str]

    @classmethod
    def unpickle(cls, pickled_string: str):
        pickled_bytes = codecs.decode(pickled_string.encode(), "base64")
        self = cls.parse_raw(pickled_bytes, allow_pickle=True, content_type="pickle")
        return self

    def pickle(self) -> str:
        pickled_bytes = pickle.dumps(self)
        pickled_string = codecs.encode(pickled_bytes, "base64").decode()
        return pickled_string

    @classmethod
    def register(cls):
        def add_meta(func: Callable):
            setattr(func, "internal_model", cls)
            return func

        return add_meta
