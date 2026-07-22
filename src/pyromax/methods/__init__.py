from .Base import BaseMaxApiMethod
from .SendMessage import SendMessageMethod
from .ForwardMessage import ForwardMessageMethod
from .EditMessage import EditMessageMethod
from .GetMessages import GetMessagesMethod
from .GetChatHistory import GetChatHistoryMethod
from .DeleteMessages import DeleteMessagesMethod
from .PinMessage import PinMessageMethod
from .GetMemberById import GetMemberByIdMethod
from .DownloadFile import DownloadFileMethod
from .UploadFile import UploadFileMethod

__all__ = [
    "BaseMaxApiMethod",
    "SendMessageMethod",
    "ForwardMessageMethod",
    "EditMessageMethod",
    "GetMessagesMethod",
    "GetChatHistoryMethod",
    "DeleteMessagesMethod",
    "PinMessageMethod",
    "GetMemberByIdMethod",
    "DownloadFileMethod",
    "UploadFileMethod",
]
