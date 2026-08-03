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
    CreateGroupMethod,
    InviteUsersToGroupMethod,
    RemoveUsersFromGroupMethod,
    ChangeGroupSettingsMethod,
    ChangeGroupProfileMethod,
    JoinGroupMethod,
    JoinChannelMethod,
    ResolveGroupByLinkMethod,
    RevokeInviteLinkMethod,
    GetChatsMethod,
    LeaveChannelMethod,
    LeaveGroupMethod,
    FetchChatsMethod,
    GetJoinRequestsMethod,
    ConfirmJoinRequestsMethod,
    DeclineJoinRequestsMethod,
    DeleteChatMethod,
    AddAdminMethod,
    Set2FaMethod,
    Remove2FaMethod,
    ChangePasswordMethod,
    Check2FaMethod,
    ApproveQrLoginMethod,
    ChangeProfileMethod,
    CreateFolderMethod,
    GetFoldersMethod,
    UpdateFolderMethod,
    DeleteFoldersMethod,
    CloseAllSessionsMethod,
    LogoutMethod,
    SetPresenceMethod,
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
        CreateGroupMethod: {
            "WEB": mapper.create_group,
            "ANDROID": mapper.create_group,
            "DESKTOP": mapper.create_group,
        },
        InviteUsersToGroupMethod: {
            "WEB": mapper.invite_users_to_group,
            "ANDROID": mapper.invite_users_to_group,
            "DESKTOP": mapper.invite_users_to_group,
        },
        RemoveUsersFromGroupMethod: {
            "WEB": mapper.remove_users_from_group,
            "ANDROID": mapper.remove_users_from_group,
            "DESKTOP": mapper.remove_users_from_group,
        },
        ChangeGroupSettingsMethod: {
            "WEB": mapper.change_group_settings,
            "ANDROID": mapper.change_group_settings,
            "DESKTOP": mapper.change_group_settings,
        },
        ChangeGroupProfileMethod: {
            "WEB": mapper.change_group_profile,
            "ANDROID": mapper.change_group_profile,
            "DESKTOP": mapper.change_group_profile,
        },
        JoinGroupMethod: {
            "WEB": mapper.join_group,
            "ANDROID": mapper.join_group,
            "DESKTOP": mapper.join_group,
        },
        JoinChannelMethod: {
            "WEB": mapper.join_channel,
            "ANDROID": mapper.join_channel,
            "DESKTOP": mapper.join_channel,
        },
        ResolveGroupByLinkMethod: {
            "WEB": mapper.resolve_group_by_link,
            "ANDROID": mapper.resolve_group_by_link,
            "DESKTOP": mapper.resolve_group_by_link,
        },
        RevokeInviteLinkMethod: {
            "WEB": mapper.revoke_invite_link,
            "ANDROID": mapper.revoke_invite_link,
            "DESKTOP": mapper.revoke_invite_link,
        },
        GetChatsMethod: {
            "WEB": mapper.get_chats,
            "ANDROID": mapper.get_chats,
            "DESKTOP": mapper.get_chats,
        },
        LeaveGroupMethod: {
            "WEB": mapper.leave_group,
            "ANDROID": mapper.leave_group,
            "DESKTOP": mapper.leave_group,
        },
        LeaveChannelMethod: {
            "WEB": mapper.leave_channel,
            "ANDROID": mapper.leave_channel,
            "DESKTOP": mapper.leave_channel,
        },
        FetchChatsMethod: {
            "WEB": mapper.fetch_chats,
            "ANDROID": mapper.fetch_chats,
            "DESKTOP": mapper.fetch_chats,
        },
        GetJoinRequestsMethod: {
            "WEB": mapper.get_join_requests,
            "ANDROID": mapper.get_join_requests,
            "DESKTOP": mapper.get_join_requests,
        },
        ConfirmJoinRequestsMethod: {
            "WEB": mapper.confirm_join_requests,
            "ANDROID": mapper.confirm_join_requests,
            "DESKTOP": mapper.confirm_join_requests,
        },
        DeclineJoinRequestsMethod: {
            "WEB": mapper.decline_join_requests,
            "ANDROID": mapper.decline_join_requests,
            "DESKTOP": mapper.decline_join_requests,
        },
        DeleteChatMethod: {
            "WEB": mapper.delete_chat,
            "ANDROID": mapper.delete_chat,
            "DESKTOP": mapper.delete_chat,
        },
        AddAdminMethod: {
            "WEB": mapper.add_admin,
            "ANDROID": mapper.add_admin,
            "DESKTOP": mapper.add_admin,
        },
        Set2FaMethod: {
            "WEB": mapper.set_2fa,
            "ANDROID": mapper.set_2fa,
            "DESKTOP": mapper.set_2fa,
        },
        Remove2FaMethod: {
            "WEB": mapper.remove_2fa,
            "ANDROID": mapper.remove_2fa,
            "DESKTOP": mapper.remove_2fa,
        },
        ChangePasswordMethod: {
            "WEB": mapper.change_password,
            "ANDROID": mapper.change_password,
            "DESKTOP": mapper.change_password,
        },
        Check2FaMethod: {
            "WEB": mapper.check_2fa,
            "ANDROID": mapper.check_2fa,
            "DESKTOP": mapper.check_2fa,
        },
        ApproveQrLoginMethod: {
            # "WEB": mapper.approve_qr_login,
            "ANDROID": mapper.approve_qr_login,
            # "DESKTOP": mapper.approve_qr_login,
        },
        ChangeProfileMethod: {
            "WEB": mapper.change_profile,
            "ANDROID": mapper.change_profile,
            "DESKTOP": mapper.change_profile,
        },
        CreateFolderMethod: {
            "WEB": mapper.create_folder,
            "ANDROID": mapper.create_folder,
            "DESKTOP": mapper.create_folder,
        },
        GetFoldersMethod: {
            "WEB": mapper.get_folders,
            "ANDROID": mapper.get_folders,
            "DESKTOP": mapper.get_folders,
        },
        UpdateFolderMethod: {
            "WEB": mapper.update_folder,
            "ANDROID": mapper.update_folder,
            "DESKTOP": mapper.update_folder,
        },
        DeleteFoldersMethod: {
            "WEB": mapper.delete_folders,
            "ANDROID": mapper.delete_folders,
            "DESKTOP": mapper.delete_folders,
        },
        CloseAllSessionsMethod: {
            "WEB": mapper.close_all_sessions,
            "ANDROID": mapper.close_all_sessions,
            "DESKTOP": mapper.close_all_sessions,
        },
        LogoutMethod: {
            "WEB": mapper.logout,
            "ANDROID": mapper.logout,
            "DESKTOP": mapper.logout,
        },
        SetPresenceMethod: {
            "WEB": mapper.set_presence,
            "ANDROID": mapper.set_presence,
            "DESKTOP": mapper.set_presence,
        },
    }

    return high_methods_registry
