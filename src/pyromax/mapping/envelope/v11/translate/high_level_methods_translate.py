from __future__ import annotations
from functools import lru_cache
from typing import Any, TYPE_CHECKING
from collections.abc import Callable, Awaitable


from .....methods import (
    BaseMaxApiMethod,
    SendMessageMethod,
    GetMemberByIdMethod,
    DownloadFileMethod,
    UploadFileMethod,
    ForwardMessageMethod,
    GetMessagesMethod,
    EditMessageMethod,
    GetChatHistoryMethod,
    DeleteMessagesMethod,
    PinMessageMethod,
    AddReactionMethod,
    RemoveReactionMethod,
    GetReactionsMethod,
    ReadMessageMethod,
)

if TYPE_CHECKING:
    from ..Mapper import Mapper


@lru_cache
def get_registry(
    mapper: Mapper,
) -> dict[type[BaseMaxApiMethod[Any]], dict[str, Callable[..., Awaitable[Any]]]]:

    high_methods_registry: dict[
        type[BaseMaxApiMethod[Any]], dict[str, Callable[..., Awaitable[Any]]]
    ] = {
        SendMessageMethod: {
            "WEB": mapper.send_message,
            "ANDROID": mapper.send_message,
            # 'IOS': mapper.send_message,
            "DESKTOP": mapper.send_message,
        },
        ForwardMessageMethod: {
            "WEB": mapper.forward_message,
            "ANDROID": mapper.forward_message,
            "DESKTOP": mapper.forward_message,
        },
        GetMessagesMethod: {
            "WEB": mapper.get_messages,
            "DESKTOP": mapper.get_messages,
            "ANDROID": mapper.get_messages,
        },
        GetMemberByIdMethod: {
            "WEB": mapper.get_member_by_id,
            # 'IOS': mapper.get_member_by_id,
            "DESKTOP": mapper.get_member_by_id,
            "ANDROID": mapper.get_member_by_id,
        },
        DownloadFileMethod: {
            "WEB": mapper.download_file,
            # 'IOS': mapper.download_file,
            "DESKTOP": mapper.download_file,
            "ANDROID": mapper.download_file,
        },
        UploadFileMethod: {
            "WEB": mapper.upload_file,
            # 'IOS': mapper.upload_file,
            "DESKTOP": mapper.upload_file,
            "ANDROID": mapper.upload_file,
        },
        EditMessageMethod: {
            "WEB": mapper.edit_message,
            "ANDROID": mapper.edit_message,
            "DESKTOP": mapper.edit_message,
        },
        GetChatHistoryMethod: {
            "WEB": mapper.get_chat_history,
            "DESKTOP": mapper.get_chat_history,
            "ANDROID": mapper.get_chat_history,
        },
        DeleteMessagesMethod: {
            "WEB": mapper.delete_messages,
            "ANDROID": mapper.delete_messages,
            "DESKTOP": mapper.delete_messages,
        },
        PinMessageMethod: {
            "WEB": mapper.pin_message,
            "ANDROID": mapper.pin_message,
            "DESKTOP": mapper.pin_message,
        },
        AddReactionMethod: {
            "WEB": mapper.add_reaction,
            "ANDROID": mapper.add_reaction,
            "DESKTOP": mapper.add_reaction,
        },
        RemoveReactionMethod: {
            "WEB": mapper.remove_reaction,
            "ANDROID": mapper.remove_reaction,
            "DESKTOP": mapper.remove_reaction,
        },
        GetReactionsMethod: {
            "WEB": mapper.get_reactions,
            "ANDROID": mapper.get_reactions,
            "DESKTOP": mapper.get_reactions,
        },
        ReadMessageMethod: {
            "WEB": mapper.read_message,
            "ANDROID": mapper.read_message,
            "DESKTOP": mapper.read_message,
        },
    }

    return high_methods_registry
