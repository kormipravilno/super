import enum
from db import db


class SelfEmployedModel(db.Model):
    __tablename__ = "self_employed"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    middle_name = db.Column(db.String)
    last_name = db.Column(db.String)

    template_id = db.Column(db.String)
    passport = db.Column(db.String)
    itn = db.Column(db.String)
    contract_number = db.Column(db.String)
    contract_date = db.Column(db.String)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._services = []

    @property
    def services(self) -> set["SelfEmployedServiceModel"]:
        return self._services

    @services.setter
    def add_service(self, service):
        self._services.append(service)


class SelfEmployedServiceType(str, enum.Enum):
    INT = "INT"
    BOOL = "BOOL"
    PHOTOS = "PHOTOS"


class SelfEmployedServiceModel(db.Model):
    __tablename__ = "self_employed_service"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.Enum(SelfEmployedServiceType), nullable=False)
    cost = db.Column(db.Float, nullable=False)

    self_employed_id = db.Column(db.Integer, db.ForeignKey("self_employed.id"))
