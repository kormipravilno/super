from db import db


class SettingsModel(db.Model):
    __tablename__ = "settings"

    key = db.Column(db.String, primary_key=True)
    value = db.Column(db.String, nullable=False)
