from db import db


class CourierModel(db.Model):
    __tablename__ = "courier"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    middle_name = db.Column(db.String)
    last_name = db.Column(db.String)

    city = db.Column(db.String, nullable=False)
    sheet_name = db.Column(db.String, nullable=False)
    folder_id = db.Column(db.String, nullable=False)
    is_gsm = db.Column(db.Boolean, nullable=False)
    gsm_cost = db.Column(db.Float, nullable=False)
    gsm_rate = db.Column(db.Float, nullable=False)
    is_to = db.Column(db.Boolean, nullable=False)
    to_cost = db.Column(db.Float)
    shift_cost = db.Column(db.Float)
