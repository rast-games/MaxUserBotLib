from .base import BaseMaxObject


class ReadState(BaseMaxObject):
    mark: int
    unread: int
    chat_id: int
    message_id: int | str
