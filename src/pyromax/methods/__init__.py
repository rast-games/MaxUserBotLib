from .Base import BaseMaxApiMethod
from .SendMessage import SendMessageMethod
from .ForwardMessage import ForwardMessageMethod
from .EditMessage import EditMessageMethod
from .GetMessages import GetMessagesMethod
from .GetChatHistory import GetChatHistoryMethod
from .DeleteMessages import DeleteMessagesMethod
from .PinMessage import PinMessageMethod
from .AddReaction import AddReactionMethod
from .RemoveReaction import RemoveReactionMethod
from .GetReactions import GetReactionsMethod
from .GetMemberById import GetMemberByIdMethod
from .DownloadFile import DownloadFileMethod
from .UploadFile import UploadFileMethod
from .ReadMessage import ReadMessageMethod
from .CreateGroup import CreateGroupMethod
from .InviteUsersToGroup import InviteUsersToGroupMethod
from .RemoveUsersFromGroup import RemoveUsersFromGroupMethod
from .ChangeGroupSettings import ChangeGroupSettingsMethod
from .ChangeGroupProfile import ChangeGroupProfileMethod
from .JoinGroup import JoinGroupMethod, JoinChannelMethod
from .ResolveGroupByLink import ResolveGroupByLinkMethod
from .RevokeInviteLink import RevokeInviteLinkMethod
from .GetChats import GetChatsMethod
from .LeaveGroup import LeaveGroupMethod, LeaveChannelMethod
from .FetchChats import FetchChatsMethod
from .GetJoinRequests import GetJoinRequestsMethod
from .ConfirmJoinRequests import ConfirmJoinRequestsMethod
from .DeclineJoinRequests import DeclineJoinRequestsMethod
from .DeleteChat import DeleteChatMethod
from .AddAdmin import AddAdminMethod
from .Set2Fa import Set2FaMethod
from .Remove2Fa import Remove2FaMethod
from .ChangePassword import ChangePasswordMethod
from .Check2Fa import Check2FaMethod
from .ApproveQrLogin import ApproveQrLoginMethod
from .ChangeProfile import ChangeProfileMethod
from .CreateFolder import CreateFolderMethod

__all__ = [
    "BaseMaxApiMethod",
    "SendMessageMethod",
    "ForwardMessageMethod",
    "EditMessageMethod",
    "GetMessagesMethod",
    "GetChatHistoryMethod",
    "DeleteMessagesMethod",
    "PinMessageMethod",
    "AddReactionMethod",
    "RemoveReactionMethod",
    "GetReactionsMethod",
    "ReadMessageMethod",
    "GetMemberByIdMethod",
    "DownloadFileMethod",
    "UploadFileMethod",
    "CreateGroupMethod",
    "InviteUsersToGroupMethod",
    "RemoveUsersFromGroupMethod",
    "ChangeGroupSettingsMethod",
    "ChangeGroupProfileMethod",
    "JoinGroupMethod",
    "JoinChannelMethod",
    "ResolveGroupByLinkMethod",
    "RevokeInviteLinkMethod",
    "GetChatsMethod",
    "LeaveGroupMethod",
    "LeaveChannelMethod",
    "FetchChatsMethod",
    "GetJoinRequestsMethod",
    "ConfirmJoinRequestsMethod",
    "DeclineJoinRequestsMethod",
    "DeleteChatMethod",
    "AddAdminMethod",
    "Set2FaMethod",
    "Remove2FaMethod",
    "ChangePasswordMethod",
    "Check2FaMethod",
    "ApproveQrLoginMethod",
    "ChangeProfileMethod",
    "CreateFolderMethod",
]
