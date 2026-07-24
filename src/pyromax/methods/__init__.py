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
]
