from __future__ import annotations
import asyncio
import logging
from typing import (
    Any,
    TYPE_CHECKING,
    AsyncGenerator,
    cast,
    Literal,
    overload,
    TypeAlias,
)
from collections.abc import Sequence, Callable, Iterable, Coroutine

from ..mixins import AsyncInitializerMixin
from ..methods import (
    SendMessageMethod,
    GetMembersByIdsMethod,
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
    GetUserMethod,
)
from ..exceptions import SendMessageError

if TYPE_CHECKING:
    from ..dispatcher.event import Update, MaxObject
    from ..protocol import Response, BaseMaxProtocol
    from ..transport import BaseTransport
    from ..mapping import BaseMapper
    from ..methods import BaseMaxApiMethod
    from ..models import (
        BaseFileAttachment,
        MessageLink,
        Message,
        EmojiReaction,
        ReadState,
        Chat,
        Profile,
        Name,
        Member,
        ChannelPermissions,
        Contact,
        RegistrationConfig,
        TwoFactorAction,
        FolderUpdate,
        FolderList,
    )
    from ..auth import AuthMiddlewareManager

from .context import *


class MaxApi(AsyncInitializerMixin):
    """Asynchronous client for MAX Messenger.

    The client initializes a transport, protocol, and mapper from the
    project registry. Initialization is asynchronous and requires the
    selected backend names to be available in the corresponding registries.

    Raises
    ------
    RuntimeError
        If a transport, protocol, or mapper name is not supported.
    """

    async def _async_init(
        self,
        device_type: str = "WEB",
        password: str | None = None,
        token: str | None = None,
        transport: str = "websocket",
        protocol: str = "EnvelopeProtocol",
        mapper: str = "EnvelopeV11",
        transport_options: dict[str, Any] | None = None,
        workflow_data: dict[Any, Any] | None = None,
        user_agent_params: dict[str, Any] | None = None,
        auth_middleware_manager: AuthMiddlewareManager | None = None,
        registration_config: RegistrationConfig | None = None,
        token_suffix: str | None = None,
        **kwargs: Any,
    ) -> None:
        if workflow_data is None:
            workflow_data = {}

        """Asynchronously initialize transport, protocol, and mapper.

        Parameters
        ----------
        device_type
            Device type reported to the API.
        password
            Optional account password.
        token
            Optional auth token.
        transport
            Transport backend name.
        protocol
            Protocol backend name.
        mapper
            Mapper backend name.
        transport_options
            Keyword arguments passed to the transport constructor.
        kwargs
            Extra keyword arguments passed to mapper initialization.
        """

        logger = logging.getLogger("MaxApi")

        if transport not in TRANSPORTS:
            raise RuntimeError(f"transport {transport} is not supported")

        if protocol not in PROTOCOLS:
            raise RuntimeError(f"protocol {protocol} is not supported")

        if mapper not in MAPPERS:
            raise RuntimeError(f"mapper {mapper} is not supported")

        logger.info("Start initialization...")
        logger.info("Initializing transport...")
        if transport_options:
            max_transport = await TRANSPORTS[transport](**transport_options)
        else:
            max_transport = await TRANSPORTS[transport]()
        logger.info("Transport initialized.")
        logger.info("Initializing protocol...")
        protocol_res: Any = await PROTOCOLS[protocol](transport=max_transport)
        max_protocol: BaseMaxProtocol[Any, Any] = protocol_res

        # max_protocol: BaseMaxProtocol[Any, Any] = await PROTOCOLS[protocol](transport=max_transport) # type: ignore
        logger.info("Protocol initialized.")
        logger.info("Initializing mapper...")
        map_class = MAPPERS[mapper]
        max_mapper = await map_class(self, protocol=max_protocol)
        logger.info("Mapper initialized.")
        await asyncio.to_thread(
            self.__init__,  # type: ignore[misc]
            protocol=max_protocol,
            password=password,
            transport=max_transport,
            mapper=max_mapper,
            transport_options=transport_options,
            token=token,
            logger=logger,
            workflow_data=workflow_data,
            device_type=device_type,
            auth_middleware_manager=auth_middleware_manager,
        )

        if token is None and self.auth_middleware_manager is not None:
            from ..models.AuthFlow import AuthFlow

            mapper_type = type(self.mapper)
            protocol_type = type(self.protocol)
            transport_type = type(self.transport)

            auth_alias = AuthFlow[
                mapper_type,  # type: ignore[valid-type]
                protocol_type,  # type: ignore[valid-type]
                transport_type,  # type: ignore[valid-type]
            ]

            async def auth_wrapped(
                auth_flow: AuthFlow[Any, Any, Any],
                _: dict[Any, Any],
            ) -> AuthFlow[Any, Any, Any]:
                return auth_flow

            wrapped = self.auth_middleware_manager.wrap_middlewares(
                self.auth_middleware_manager,
                auth_wrapped,
            )

            auth_alias.model_rebuild(
                _types_namespace={
                    "MaxApi": type(self),
                }
            )
            # auth_constructor.model_rebuild()

            flow = auth_alias(
                max_api=self,
                mapper=self.mapper,
                protocol=self.protocol,
                transport=self.transport,
            )

            data = {
                type(self): self,
                mapper_type: self.mapper,
                protocol_type: self.protocol,
                transport_type: self.transport,
            }

            resolved_flow = await wrapped(flow, cast(dict[Any, Any], data))
            token = resolved_flow.token

        await self.mapper.initialize_client(
            token=token,
            device_type=device_type,
            password=password,
            user_agent_params=user_agent_params,
            registration_config=registration_config,
            token_suffix=token_suffix,
            **kwargs,
        )

    def __init__(
        self,
        device_type: str = "WEB",
        password: str | None = None,
        transport: BaseTransport | None = None,
        protocol: BaseMaxProtocol[Any, Any] | None = None,
        mapper: BaseMapper[Any, Any] | None = None,
        transport_options: dict[str, Any] | None = None,
        token: str | None = None,
        logger: logging.Logger | None = None,
        workflow_data: dict[Any, Any] | None = None,
        auth_middleware_manager: AuthMiddlewareManager | None = None,
        registration_config: RegistrationConfig | None = None,
        token_suffix: str | None = None,
        **kwargs: Any,
    ) -> None:

        if workflow_data is None:
            workflow_data = {}

        if logger is None:
            logger = logging.getLogger("MaxApi")

        if transport is None or protocol is None or mapper is None:
            raise RuntimeError("transport or protocol or mapper cannot be None")

        self.transport = transport
        self.transport_options = transport_options
        self.protocol = protocol
        self.mapper = mapper
        self.token = token
        self.password = password
        self.id: int | None = None
        self.phone: str | None = None

        self.me: Profile | None = None
        self.chats: list[Chat] | None = None
        self.names: list[Name] | None = None
        self.contacts: list[Contact | None] = []
        self.users: dict[int, Contact] = {}
        self.messages: dict[int, list[Message]]

        self.__logger: logging.Logger | None = logger
        self.workflow_data = workflow_data
        self.auth_middleware_manager = auth_middleware_manager

    async def __call__(
        self, class_of_method: type[BaseMaxApiMethod[Any]], *args: Any, **kwargs: Any
    ) -> Any:
        if self.__logger is None:
            raise RuntimeError(
                "Try a call method before initialization, because logger has not been initialized"
            )
        self.__logger.debug("Calling MaxApi method: %s", class_of_method.__name__)
        method = class_of_method().as_(self)

        return await method(*args, **kwargs)

    def listen_updates(
        self, context: Any
    ) -> tuple[Callable[[Response], MaxObject], AsyncGenerator[Response, None]]:
        """Yield incoming updates forever.

        Parameters
        ----------
        context
            Runtime context passed to the mapper.

        Returns
        -------
        AsyncGenerator[Update, None]
            Stream of incoming updates.
        """
        return self.mapper.listen_updates(context=context)

    async def download_file(
        self, file: BaseFileAttachment
    ) -> tuple[bytes, dict[str, str]] | tuple[None, None]:
        return cast(
            tuple[bytes, dict[str, str]] | tuple[None, None],
            await self(
                DownloadFileMethod,
                file=file,
            ),
        )

    async def upload_file(
        self, data: bytes | None, typeof: type[BaseFileAttachment], **kwargs: Any
    ) -> list[BaseFileAttachment | Any]:
        from ..models import BaseFileAttachment

        return cast(
            list[BaseFileAttachment | Any],
            await self(
                UploadFileMethod,
                data=data,
                typeof=typeof,
                **kwargs,
            ),
        )

    async def send_message(
        self,
        chat_id: int,
        text: str = "",
        attaches: list[BaseFileAttachment] | None = None,
        link: MessageLink | None = None,
    ) -> Message | None:
        """Send a message to a chat.

        Parameters
        ----------
        chat_id
            Target chat identifier.
        text
            Message text.
        attaches
            Optional list of attachments.
        link
            Optional message link object.

        Returns
        -------
        Any
            API response returned by the mapper.

        Raises
        ------
        SendMessageError
            If message sending fails.
        """
        from ..models import Message

        try:
            return cast(
                Message | None,
                await self(
                    SendMessageMethod,
                    text=text,
                    chat_id=chat_id,
                    attaches=attaches,
                    link=link,
                ),
            )
        except SendMessageError as e:
            if self.__logger is None:
                raise AttributeError("logger not initialized in MaxApi instance")
            self.__logger.warning("Failed to send message: %s", e)
            raise e

    async def forward_message(
        self,
        message_id: int | str,
        to_chat_id: int,
        from_chat_id: int,
    ) -> Message | None:
        try:
            from ..models import Message

            return cast(
                Message | None,
                await self(
                    ForwardMessageMethod,
                    message_id=message_id,
                    to_chat_id=to_chat_id,
                    from_chat_id=from_chat_id,
                ),
            )
        except SendMessageError as e:
            if self.__logger is None:
                raise AttributeError("logger not initialized in MaxApi instance")
            self.__logger.warning("Failed to forward message: %s", e)
            raise e

    async def edit_message(
        self,
        chat_id: int,
        message_id: int | str,
        text: str | None = None,
        attaches: list[BaseFileAttachment] | None = None,
        **kwargs: Any,
    ) -> Message:
        from ..models import Message

        return cast(
            Message,
            await self(
                EditMessageMethod,
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                attaches=attaches,
            ),
        )

    async def get_messages(
        self, chat_id: int, message_ids: Iterable[str] | Iterable[int]
    ) -> list[Message]:
        from ..models import Message

        return cast(
            list[Message],
            await self(
                GetMessagesMethod,
                chat_id=chat_id,
                message_ids=message_ids,
            ),
        )

    @overload
    async def get_chat_history(
        self,
        chat_id: int,
        forward: int = ...,
        backward: int = ...,
        backward_time: int = ...,
        forward_time: int = ...,
        from_time: int | None = ...,
        item_type: Literal["DELAYED", "REGULAR"] = ...,
        get_chat: bool = ...,
        get_messages: Literal[True] = True,
        interactive: bool = ...,
    ) -> list[Message]:
        pass

    @overload
    async def get_chat_history(
        self,
        chat_id: int,
        forward: int = ...,
        backward: int = ...,
        backward_time: int = ...,
        forward_time: int = ...,
        from_time: int | None = None,
        item_type: Literal["DELAYED", "REGULAR"] = ...,
        get_chat: bool = ...,
        get_messages: Literal[False] = False,
        interactive: bool = ...,
    ) -> list[str]:
        pass

    async def get_chat_history(
        self,
        chat_id: int,
        forward: int = 0,
        backward: int = 40,
        backward_time: int = 0,
        forward_time: int = 0,
        from_time: int | None = None,
        item_type: Literal["DELAYED", "REGULAR"] = "REGULAR",
        get_chat: bool = False,
        get_messages: bool = True,
        interactive: bool = False,
    ) -> list[Message] | list[str]:

        from ..models import Message

        return cast(
            list[Message] | list[str],
            await self(
                GetChatHistoryMethod,
                chat_id=chat_id,
                forward=forward,
                backward=backward,
                backward_time=backward_time,
                forward_time=forward_time,
                from_time=from_time,
                item_type=item_type,
                get_chat=get_chat,
                get_messages=get_messages,
                interactive=interactive,
            ),
        )

    async def delete_messages(
        self,
        chat_id: int,
        message_ids: list[str] | list[int],
        for_me: bool = False,
    ) -> None:
        return cast(
            None,
            await self(
                DeleteMessagesMethod,
                chat_id=chat_id,
                message_ids=message_ids,
                for_me=for_me,
            ),
        )

    async def pin_message(
        self, chat_id: int, message_id: int | str, notify: bool = True
    ) -> None:

        return cast(
            None,
            await self(
                PinMessageMethod,
                chat_id=chat_id,
                message_id=message_id,
                notify=notify,
            ),
        )

    async def add_reaction(
        self,
        chat_id: int,
        message_id: int | str,
        reaction_id: str,
        reaction_type: str = "EMOJI",
    ) -> EmojiReaction | None:
        """
        Parameters
        ----------
        chat_id
            int
        message_id
            int | str
        reaction_id
            str
        reaction_type
            str

        Returns
        -------
        EmojiReaction | None
            info about reaction or None if cannot get this info

        Raises
        -------
            ReactionMapperError
                if adding reaction failed
        """

        from ..models import EmojiReaction

        return cast(
            EmojiReaction | None,
            await self(
                AddReactionMethod,
                chat_id=chat_id,
                message_id=message_id,
                reaction_id=reaction_id,
                reaction_type=reaction_type,
            ),
        )

    async def remove_reaction(
        self,
        chat_id: int,
        message_id: int | str,
    ) -> EmojiReaction | None:
        from ..models import EmojiReaction

        return cast(
            EmojiReaction | None,
            await self(RemoveReactionMethod, chat_id=chat_id, message_id=message_id),
        )

    async def get_reactions(
        self,
        chat_id: int,
        message_ids: list[str] | list[int],
    ) -> dict[str, EmojiReaction] | None:
        from ..models import EmojiReaction

        return cast(
            dict[str, EmojiReaction] | None,
            await self(GetReactionsMethod, chat_id=chat_id, message_ids=message_ids),
        )

    async def read_message(
        self,
        chat_id: int,
        message_id: int | str,
        typeof: str = "READ_MESSAGE",
        mark: int | None = None,
    ) -> ReadState:
        from ..models import ReadState

        return cast(
            ReadState,
            await self(
                ReadMessageMethod,
                chat_id=chat_id,
                message_id=message_id,
                typeof=typeof,
                mark=mark,
            ),
        )

    async def create_group(
        self,
        title: str,
        participant_ids: list[int] | None = None,
        notify: bool = True,
        chat_type: str = "CHAT",
        event: str = "new",
        typeof: str = "CONTROL",
    ) -> tuple[Chat, Message] | tuple[None, None]:
        from ..models import Chat, Message

        return cast(
            tuple[Chat, Message] | tuple[None, None],
            await self(
                CreateGroupMethod,
                title=title,
                participant_ids=participant_ids,
                notify=notify,
                chat_type=chat_type,
                event=event,
                typeof=typeof,
            ),
        )

    async def invite_users_to_group(
        self,
        chat_id: int,
        user_ids: list[int],
        show_history: bool = True,
    ) -> Chat | None:
        from ..models import Chat

        return cast(
            Chat | None,
            await self(
                InviteUsersToGroupMethod,
                chat_id=chat_id,
                user_ids=user_ids,
                show_history=show_history,
            ),
        )

    async def remove_users_from_group(
        self,
        chat_id: int,
        user_ids: list[int] | list[str],
        clean_msg_period: int,
    ) -> Chat | None:
        from ..models import Chat

        return cast(
            Chat | None,
            await self(
                RemoveUsersFromGroupMethod,
                chat_id=chat_id,
                user_ids=user_ids,
                clean_msg_period=clean_msg_period,
            ),
        )

    async def change_group_settings(
        self,
        chat_id: int,
        all_can_pin_message: bool | None = None,
        only_owner_can_change_icon_title: bool | None = None,
        only_admin_can_add_member: bool | None = None,
        only_admin_can_call: bool | None = None,
        member_can_see_private_link: bool | None = None,
    ) -> Chat | None:
        from ..models import Chat

        return cast(
            Chat | None,
            await self(
                ChangeGroupSettingsMethod,
                chat_id=chat_id,
                all_can_pin_message=all_can_pin_message,
                only_owner_can_change_icon_title=only_owner_can_change_icon_title,
                only_admin_can_add_member=only_admin_can_add_member,
                only_admin_can_call=only_admin_can_call,
                member_can_see_private_link=member_can_see_private_link,
            ),
        )

    async def change_group_profile(
        self,
        chat_id: int,
        name: str | None = None,
        description: str | None = None,
    ) -> Chat | None:
        from ..models import Chat

        return cast(
            Chat | None,
            await self(
                ChangeGroupProfileMethod,
                chat_id=chat_id,
                name=name,
                description=description,
            ),
        )

    async def join_group(self, link: str) -> Chat:
        from ..models import Chat

        return cast(
            Chat,
            await self(JoinGroupMethod, link=link),
        )

    async def join_channel(self, link: str) -> Chat:
        from ..models import Chat

        return cast(
            Chat,
            await self(JoinChannelMethod, link=link),
        )

    async def resolve_group_by_link(self, link: str) -> Chat | None:
        from ..models import Chat

        return cast(
            Chat | None,
            await self(ResolveGroupByLinkMethod, link=link),
        )

    async def revoke_invite_link(self, chat_id: int) -> Chat:
        from ..models import Chat

        return cast(
            Chat,
            await self(RevokeInviteLinkMethod, chat_id=chat_id),
        )

    async def get_chats(self, chat_ids: Iterable[int]) -> list[Chat]:
        from ..models import Chat

        return cast(
            list[Chat],
            await self(GetChatsMethod, chat_ids=chat_ids),
        )

    async def get_chat(self, chat_id: int) -> Chat:
        chats = await self.get_chats([chat_id])
        if not chats:
            raise ValueError("Chat not found")
        return chats[0]

    async def leave_group(self, chat_id: int) -> Message | None:
        from ..models import Message

        return cast(
            Message | None,
            await self(
                LeaveGroupMethod,
                chat_id=chat_id,
            ),
        )

    async def leave_channel(self, chat_id: int) -> Message | None:
        from ..models import Message

        return cast(
            Message | None,
            await self(
                LeaveChannelMethod,
                chat_id=chat_id,
            ),
        )

    async def fetch_chats(self, marker: int | None = None) -> list[Chat]:
        from ..models import Chat

        return cast(
            list[Chat],
            await self(FetchChatsMethod, marker=marker),
        )

    async def get_join_requests(self, chat_id: int, count: int = 100) -> list[Member]:
        from ..models import Member

        return cast(
            list[Member],
            await self(
                GetJoinRequestsMethod,
                chat_id=chat_id,
                count=count,
            ),
        )

    async def confirm_join_requests(
        self,
        chat_id: int,
        user_ids: Iterable[int],
        show_history: bool = True,
    ) -> Chat | None:
        from ..models import Chat

        return cast(
            Chat | None,
            await self(
                ConfirmJoinRequestsMethod,
                chat_id=chat_id,
                user_ids=user_ids,
                show_history=show_history,
            ),
        )

    async def confirm_join_request(
        self,
        chat_id: int,
        user_id: int,
        show_history: bool = True,
    ) -> Chat | None:
        return await self.confirm_join_requests(
            chat_id=chat_id,
            user_ids=[user_id],
            show_history=show_history,
        )

    async def decline_join_requests(
        self,
        chat_id: int,
        user_ids: Iterable[int],
    ) -> Chat | None:
        from ..models import Chat

        return cast(
            Chat | None,
            await self(
                DeclineJoinRequestsMethod,
                chat_id=chat_id,
                user_ids=user_ids,
            ),
        )

    async def decline_join_request(
        self,
        chat_id: int,
        user_id: int,
    ) -> Chat | None:
        return await self.decline_join_requests(
            chat_id=chat_id,
            user_ids=[user_id],
        )

    async def delete_chat(
        self,
        chat_id: int,
        last_event_time: int | None = None,
        for_all: bool = True,
    ) -> None:
        return cast(
            None,
            await self(
                DeleteChatMethod,
                chat_id=chat_id,
                last_event_time=last_event_time,
                for_all=for_all,
            ),
        )

    async def add_admin(
        self, chat_id: int, user_id: int, permissions: Iterable[ChannelPermissions]
    ) -> None:
        return cast(
            None,
            await self(
                AddAdminMethod,
                chat_id=chat_id,
                user_id=user_id,
                permissions=permissions,
            ),
        )

    async def set_2fa(
        self,
        password: str,
        email: str | None = None,
        hint: str | None = None,
        email_code_getter: Callable[[str], Coroutine[Any, Any, str]] | None = None,
        two_factor_actions: list[TwoFactorAction] | None = None,
    ) -> None:
        return cast(
            None,
            await self(
                Set2FaMethod,
                password=password,
                email=email,
                hint=hint,
                email_code_getter=email_code_getter,
                two_factor_actions=two_factor_actions,
            ),
        )

    async def remove_2fa(
        self,
        password: str,
        two_factor_actions: list[TwoFactorAction] | None = None,
        remove_2fa: bool = True,
    ) -> None:
        return cast(
            None,
            await self(
                Remove2FaMethod,
                password=password,
                two_factor_actions=two_factor_actions,
                remove_2fa=remove_2fa,
            ),
        )

    async def change_password(
        self,
        password_old: str,
        password_new: str,
        hint: str | None = None,
        two_factor_actions: list[TwoFactorAction] | None = None,
    ) -> None:
        return cast(
            None,
            await self(
                ChangePasswordMethod,
                password_old=password_old,
                password_new=password_new,
                hint=hint,
                two_factor_actions=two_factor_actions,
            ),
        )

    async def check_2fa(self) -> bool:
        return cast(
            bool,
            await self(
                Check2FaMethod,
            ),
        )

    async def approve_qr_login(self, qr_link: str) -> None:
        return cast(
            None,
            await self(
                ApproveQrLoginMethod,
                qr_link=qr_link,
            ),
        )

    async def change_profile(
        self,
        first_name: str,
        last_name: str | None = None,
        description: str | None = None,
        photo: bytes | None = None,
        file_name: str | None = None,
        photo_token: str | None = None,
    ) -> Profile:
        from ..models import Profile

        return cast(
            Profile,
            await self(
                ChangeProfileMethod,
                first_name=first_name,
                last_name=last_name,
                description=description,
                photo=photo,
                file_name=file_name,
                photo_token=photo_token,
            ),
        )

    async def create_folder(
        self,
        title: str,
        chat_include: list[int],
        filters: list[Any] | None = None,
        folder_id: str | None = None,
    ) -> FolderUpdate:
        from ..models import FolderUpdate

        return cast(
            FolderUpdate,
            await self(
                CreateFolderMethod,
                title=title,
                chat_include=chat_include,
                filters=filters,
                folder_id=folder_id,
            ),
        )

    async def get_folders(self, folder_sync: int = 0) -> FolderList:
        from ..models import FolderList

        return cast(
            FolderList,
            await self(
                GetFoldersMethod,
                folder_sync=folder_sync,
            ),
        )

    async def update_folder(
        self,
        folder_id: str,
        title: str,
        chat_include: list[int] | None = None,
        filters: list[Any] | None = None,
        options: list[Any] | None = None,
    ) -> FolderUpdate:
        from ..models import FolderUpdate

        return cast(
            FolderUpdate,
            await self(
                UpdateFolderMethod,
                title=title,
                chat_include=chat_include,
                filters=filters,
                folder_id=folder_id,
                options=options,
            ),
        )

    async def delete_folders(
        self,
        folder_ids: list[str] | None = None,
    ) -> FolderUpdate:
        from ..models import FolderUpdate

        return cast(
            FolderUpdate,
            await self(
                DeleteFoldersMethod,
                folder_ids=folder_ids,
            ),
        )

    async def delete_folder(self, folder_id: str) -> FolderUpdate:
        return await self.delete_folders(folder_ids=[folder_id])

    async def close_all_sessions(self) -> bool:
        return cast(
            bool,
            await self(
                CloseAllSessionsMethod,
            ),
        )

    async def logout(self) -> None:
        return cast(None, await self(LogoutMethod))

    async def set_presence(self, online: bool) -> None:
        return cast(
            None,
            await self(
                SetPresenceMethod,
                online=online,
            ),
        )

    async def get_members_by_ids(self, member_ids: list[int]) -> Sequence[Contact]:
        from ..models import Contact

        contacts = cast(
            Sequence[Contact],
            await self(
                GetMembersByIdsMethod,
                member_ids=member_ids,
            ),
        )
        return contacts
        # return await self.mapper.get_member_by_id(member_id)

    async def get_member_by_id(self, member_id: int) -> Contact | None:
        contacts = await self.get_members_by_ids(member_ids=[member_id])
        return contacts[0] if contacts else None

    async def get_user(self, user_id: int) -> Contact | None:
        from ..models import Contact

        user = cast(
            Contact,
            await self(
                GetUserMethod,
                user_id=user_id,
            ),
        )
        return user
