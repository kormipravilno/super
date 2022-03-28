from db import db


class AdminModel(db.Model):
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    middle_name = db.Column(db.String)
    last_name = db.Column(db.String)
