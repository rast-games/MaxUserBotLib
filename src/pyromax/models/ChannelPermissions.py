from enum import Enum

from .base import BaseMaxObject


class ChannelPermissions(Enum):
    ADD_REMOVE_MEMBER = "add_remove_member"
    ADD_ADMIN = "add_admin"
    CHANGE_CHAT_INFO = "change_chat_info"
    PIN_MESSAGE = "pin_message"
    POST_MESSAGE = "post_message"
    EDIT_MESSAGE = "edit_message"
    DELETE_MESSAGE = "delete_message"
