from db import db


class ReportChatModel(db.Model):
    __tablename__ = "report_chat"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
