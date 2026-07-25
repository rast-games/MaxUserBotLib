from typing import cast, Literal

from ...payloads.models import (
    MessageLinkMappingModel,
    MessageMappingModel,
    ChannelPermissionsMappingModel,
)
from ......models import Message, ChannelPermissions


def reverse_translate_message(message: Message) -> MessageMappingModel | None:
    if not message:
        return None
    message_link = message.link
    if message.status not in ("USER", "EDITED", "REPLY"):
        status = "USER"
    else:
        status = message.status
    if message_link:
        inner_message = message_link.message

        if inner_message is None:
            raise RuntimeError(
                "In message link exists, but not bound to another message"
            )

        return MessageMappingModel(
            id=message.message_id,
            status=cast(Literal["USER", "EDITED", "REPLY"], status),
            time=message.time,
            type=message.type,
            text=message.text if message.text else None,
            elements=message.elements if message.elements and message.text else None,
            chat_id=message.chat_id,
            link=MessageLinkMappingModel(
                type=message_link.type,
                message=reverse_translate_message(inner_message),
            ),
        )
    return MessageMappingModel(
        id=message.message_id,
        status=cast(Literal["USER", "EDITED", "REPLY"], status),
        time=message.time,
        type=message.type,
        text=message.text if message.text else None,
        elements=message.elements if message.elements and message.text else None,
        chat_id=message.chat_id,
    )


channel_permissions_map: dict[ChannelPermissions, ChannelPermissionsMappingModel] = {
    ChannelPermissions.ADD_REMOVE_MEMBER: ChannelPermissionsMappingModel.ADD_REMOVE_MEMBER,
    ChannelPermissions.ADD_ADMIN: ChannelPermissionsMappingModel.ADD_ADMIN,
    ChannelPermissions.CHANGE_CHAT_INFO: ChannelPermissionsMappingModel.CHANGE_CHAT_INFO,
    ChannelPermissions.PIN_MESSAGE: ChannelPermissionsMappingModel.PIN_MESSAGE,
    ChannelPermissions.POST_MESSAGE: ChannelPermissionsMappingModel.POST_MESSAGE,
    ChannelPermissions.EDIT_MESSAGE: ChannelPermissionsMappingModel.EDIT_MESSAGE,
    ChannelPermissions.DELETE_MESSAGE: ChannelPermissionsMappingModel.DELETE_MESSAGE,
}


def reverse_translate_channel_permissions(
    channel_permissions: ChannelPermissions,
) -> ChannelPermissionsMappingModel:
    return channel_permissions_map[channel_permissions]
