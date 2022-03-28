from models.chats import ReportChatModel
from common.schemas import ReportChatSchema
from .base import CRUDBase


class ReportChatCRUD(CRUDBase[ReportChatModel, ReportChatSchema, ReportChatSchema]):
    pass


report_chat = ReportChatCRUD(ReportChatModel, ReportChatSchema)
