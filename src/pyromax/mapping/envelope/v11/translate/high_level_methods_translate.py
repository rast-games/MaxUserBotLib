from __future__ import annotations
from functools import lru_cache
from typing import Any, TYPE_CHECKING
from collections.abc import Callable, Awaitable


from .....methods import BaseMaxApiMethod, SendMessageMethod, GetMemberByIdMethod, DownloadFileMethod, UploadFileMethod

if TYPE_CHECKING:
    from ..Mapper import Mapper



@lru_cache
def get_registry(mapper: Mapper) -> dict[type[BaseMaxApiMethod[Any]], dict[str, Callable[..., Awaitable[Any]]]]:

    high_methods_registry: dict[type[BaseMaxApiMethod[Any]], dict[str, Callable[..., Awaitable[Any]]]] = {
        SendMessageMethod: {
            'WEB': mapper.send_message,
            'ANDROID': mapper.send_message,
            'IOS': mapper.send_message,
            'DESKTOP': mapper.send_message
        },
        GetMemberByIdMethod: {
            'WEB': mapper.get_member_by_id,
            'IOS': mapper.get_member_by_id,
            'DESKTOP': mapper.get_member_by_id,
            'ANDROID': mapper.get_member_by_id,
        },
        DownloadFileMethod: {
            'WEB': mapper.download_file,
            'IOS': mapper.download_file,
            'DESKTOP': mapper.download_file,
            'ANDROID': mapper.download_file,
        },
        UploadFileMethod: {
            'WEB': mapper.upload_file,
            'IOS': mapper.upload_file,
            'DESKTOP': mapper.upload_file,
            'ANDROID': mapper.upload_file,
        }
    }

    return high_methods_registry