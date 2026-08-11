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
    CreatePollMethod,
    VotePollMethod,
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
    ChangeProfileSettingsMethod,
    GetUsersMethod,
    SearchByPhoneMethod,
    GetSessionsMethod,
    GetChatIdMethod,
    AddContactMethod,
    RemoveContactMethod,
    ImportContactsMethod,
)
from ..exceptions import SendMessageError, MapperApiError, ReactionError

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
        Session,
        ContactInfo,
        Poll,
        PollState,
        PrivacySettings,
    )
    from ..auth import AuthMiddlewareManager

from .context import *


class MaxApi(AsyncInitializerMixin):
    """Asynchronous client for MAX Messenger.

    The client initializes a transport, protocol, and mapper from the
    project registry. Initialization is asynchronous and requires the
    selected backend names to be available in the corresponding registries.

    :raises RuntimeError: If a transport, protocol, or mapper name is not supported.
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
        """Asynchronously initialize transport, protocol, and mapper.

        :param device_type: Device type reported to the API.
        :type device_type: str
        :param password: Optional account password.
        :type password: str | None
        :param token: Optional auth token.
        :type token: str | None
        :param transport: Transport backend name.
        :type transport: str
        :param protocol: Protocol backend name.
        :type protocol: str
        :param mapper: Mapper backend name.
        :type mapper: str
        :param transport_options: Keyword arguments passed to the transport constructor.
        :type transport_options: dict[str, Any] | None
        :param kwargs: Extra keyword arguments passed to mapper initialization.
        :type kwargs: Any

        :param workflow_data: dict[Any, Any] global workflow data.
        :type workflow_data: dict[Any, Any] | None
        :param user_agent_params: dict[str, Any] params of user agent.
        :type user_agent_params: dict[str, Any] | None
        :param auth_middleware_manager: AuthMiddlewareManager instance of auth middleware manager.
        :type auth_middleware_manager: AuthMiddlewareManager | None
        :param registration_config: instance of RegistrationConfig for register account.
        :type registration_config: RegistrationConfig | None
        :param token_suffix: The token suffix value.
        :type token_suffix: str | None
        :raises RuntimeError: If the requested action cannot be completed.
        """
        if workflow_data is None:
            workflow_data = {}

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
                """Auth wrapped.

                :param auth_flow: AuthFlow[Any, Any, Any] instance to process.
                :type auth_flow: AuthFlow[Any, Any, Any]
                :param _: dict[Any, Any] instance to process.
                :type _: dict[Any, Any]
                :returns: The resulting AuthFlow[Any, Any, Any] value.
                :rtype: AuthFlow[Any, Any, Any]
                """
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

            flow = auth_alias(
                mapper=self.mapper,
                protocol=self.protocol,
                transport=self.transport,
            )
            flow.as_(self)

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
        """Initialize the max api.

        :param device_type: The device type value.
        :type device_type: str
        :param password: Account password.
        :type password: str | None
        :param transport: Transport backend or transport instance.
        :type transport: BaseTransport | None
        :param protocol: Protocol backend or protocol instance.
        :type protocol: BaseMaxProtocol[Any, Any] | None
        :param mapper: Mapper backend or mapper instance.
        :type mapper: BaseMapper[Any, Any] | None
        :param transport_options: dict[str, Any] instance to process.
        :type transport_options: dict[str, Any] | None
        :param token: Authentication token.
        :type token: str | None
        :param logger: Logger used for diagnostic messages.
        :type logger: logging.Logger | None
        :param workflow_data: dict[Any, Any] instance to process.
        :type workflow_data: dict[Any, Any] | None
        :param auth_middleware_manager: AuthMiddlewareManager instance to process.
        :type auth_middleware_manager: AuthMiddlewareManager | None
        :param registration_config: RegistrationConfig instance to process.
        :type registration_config: RegistrationConfig | None
        :param token_suffix: The token suffix value.
        :type token_suffix: str | None
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :raises RuntimeError: If transport or protocol or mapper cannot be None.
        """
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

        self.__logger: logging.Logger | None = logger
        self.workflow_data = workflow_data
        self.auth_middleware_manager = auth_middleware_manager

    async def __call__(
        self, class_of_method: type[BaseMaxApiMethod[Any]], *args: Any, **kwargs: Any
    ) -> Any:
        """Invoke the max api.

        :param class_of_method: MAX API method class to instantiate and execute.
        :type class_of_method: type[BaseMaxApiMethod[Any]]
        :param args: Positional arguments forwarded to the wrapped callable.
        :type args: Any
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :returns: The value returned by the wrapped callable or backend.
        :rtype: Any
        :raises RuntimeError: If try a call method before initialization, because logger has not been initialized.
        """
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

        :param context: Runtime context passed to the mapper.
        :type context: Any

        :returns: Stream of incoming updates.
        :rtype: tuple[Callable[[Response], MaxObject], AsyncGenerator[Response, None]]
        """
        return self.mapper.listen_updates(context=context)

    async def download_file(
        self, file: BaseFileAttachment
    ) -> tuple[bytes, dict[str, str]] | tuple[None, None]:
        """Download file.

        :param file: File attachment to process.
        :type file: BaseFileAttachment
        :returns: The resulting tuple[bytes, dict[str, str]] | tuple[None, None] value is request headers | None semantic.
        :rtype: tuple[bytes, dict[str, str]] | tuple[None, None]
        """
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
        """Upload file.

        :param data: Contextual data passed through the processing pipeline.
        :type data: bytes | None
        :param typeof: Attachment class that determines the upload type.
        :type typeof: type[BaseFileAttachment]
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :returns: The resulting collection.
        :rtype: list[BaseFileAttachment | Any]
        """
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
        notify: bool = True,
    ) -> Message | None:
        """Send a message to a chat.

        :param chat_id: Target chat identifier.
        :type chat_id: int
        :param text: Message text.
        :type text: str
        :param attaches: Optional list of attachments.
        :type attaches: list[BaseFileAttachment] | None
        :param link: Optional message link object.
        :type link: MessageLink | None

        :returns: API response returned by the mapper.
        :rtype: Message | None

        :raises SendMessageError: If message sending fails.

        :param notify: Whether MAX should notify affected users.
        :type notify: bool
        :raises AttributeError: If logger not initialized in MaxApi instance.
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
                    notify=notify,
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
        notify: bool = True,
    ) -> Message | None:
        """Forward message.

        :param message_id: Identifier of the message.
        :type message_id: int | str
        :param to_chat_id: Identifier of the destination chat.
        :type to_chat_id: int
        :param from_chat_id: Identifier of the source chat.
        :type from_chat_id: int
        :param notify: Whether MAX should notify affected users.
        :type notify: bool
        :returns: The resulting Message | None value.
        :rtype: Message | None
        :raises AttributeError: If logger not initialized in MaxApi instance.
        """
        try:
            from ..models import Message

            return cast(
                Message | None,
                await self(
                    ForwardMessageMethod,
                    message_id=message_id,
                    to_chat_id=to_chat_id,
                    from_chat_id=from_chat_id,
                    notify=notify,
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
        """Edit message.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_id: Identifier of the message.
        :type message_id: int | str
        :param text: Message or textual content.
        :type text: str | None
        :param attaches: Attachments associated with the message.
        :type attaches: list[BaseFileAttachment] | None
        # :param kwargs: Keyword arguments forwarded to the wrapped callable.
        # :type kwargs: Any
        :returns: The resulting Message value.
        :rtype: Message
        """
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
        """Retrieve messages.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_ids: Identifiers of the messages.
        :type message_ids: Iterable[str] | Iterable[int]
        :returns: The resulting collection.
        :rtype: list[Message]
        """
        from ..models import Message

        return cast(
            list[Message],
            await self(
                GetMessagesMethod,
                chat_id=chat_id,
                message_ids=message_ids,
            ),
        )

    async def get_message(self, chat_id: int, message_id: int | str) -> Message | None:
        """Retrieve message.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_id: Identifier of the message.
        :type message_id: int | str
        :returns: The resulting Message | None value.
        :rtype: Message | None
        """
        msgs = await self.get_messages(chat_id=chat_id, message_ids=[message_id])
        return msgs[0] if msgs else None

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
        get_messages: bool = ...,
        interactive: bool = ...,
    ) -> list[Message] | list[str]: ...

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
        """Retrieve chat history.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param forward: How many messages to load ahead from ``from_time``.
        :type forward: int
        :param backward: How many messages to load back from ``from_time``.
        :type backward: int
        :param backward_time: Look-back time window in milliseconds.
        :type backward_time: int
        :param forward_time: Forward time window in milliseconds.
        :type forward_time: int
        :param from_time: The reference point in Unix time (milliseconds). If ``None``, the current moment is used.
        :type from_time: int | None
        :param item_type: History item type.
        :type item_type: Literal['DELAYED', 'REGULAR']
        :param get_chat: Request chat data along with the history.
        :type get_chat: bool
        :param get_messages: The get messages value.
        :type get_messages: bool
        :param interactive: Request the messages themselves.
        :type interactive: bool
        :returns: Message collection if get_messages is True else message ids collection.
        :rtype: list[Message] | list[str]
        """
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
        """Delete messages.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_ids: Identifiers of the messages.
        :type message_ids: list[str] | list[int]
        :param for_me: Delete only for the current account.
        :type for_me: bool
        """
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
        """Pin message.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_id: Identifier of the message.
        :type message_id: int | str
        :param notify: Whether MAX should notify affected users.
        :type notify: bool
        """
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
        """Add an emoji reaction to a message.

        :param chat_id: Identifier of the chat containing the message.
        :type chat_id: int
        :param message_id: int | str
        :type message_id: int | str
        :param reaction_id: str
        :type reaction_id: str
        :param reaction_type: str
        :type reaction_type: str

        :returns: info about reaction or None if cannot get this info
        :rtype: EmojiReaction | None

        :raises ReactionError: if adding reaction failed
        """

        from ..models import EmojiReaction

        try:
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
        except MapperApiError as e:
            raise ReactionError("add reaction failed") from e

    async def remove_reaction(
        self,
        chat_id: int,
        message_id: int | str,
    ) -> EmojiReaction | None:
        """Remove reaction.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_id: Identifier of the message.
        :type message_id: int | str
        :returns: The resulting EmojiReaction | None value.
        :rtype: EmojiReaction | None
        """
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
        """Retrieve reactions.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_ids: Identifiers of the messages.
        :type message_ids: list[str] | list[int]
        :returns: The resulting dict[<message_id>, <EmojiReaction for this message>] | None value.
        :rtype: dict[str, EmojiReaction] | None
        """
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
        """Read message.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_id: Identifier of the message.
        :type message_id: int | str
        :param typeof: Attachment class that determines the upload type.
        :type typeof: str
        :param mark: The mark value.
        :type mark: int | None
        :returns: The resulting ReadState value.
        :rtype: ReadState
        """
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

    async def create_poll(
        self,
        poll: Poll,
    ) -> Poll:
        """Create poll.

        :param poll: Poll instance to process.
        :type poll: Poll
        :returns: The resulting Poll value what can be send with message in send_message method.
        :rtype: Poll
        """
        from ..models import Poll

        return cast(
            Poll,
            await self(
                CreatePollMethod,
                poll=poll,
            ),
        )

    async def vote_poll(
        self,
        chat_id: int,
        message_id: int | str,
        poll_id: int,
        answer_ids: list[int],
    ) -> PollState:
        """Submit a vote for poll.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param message_id: Identifier of the message.
        :type message_id: int | str
        :param poll_id: Identifier of the poll.
        :type poll_id: int
        :param answer_ids: Identifiers of the answer objects.
        :type answer_ids: list[int]
        :returns: The resulting PollState value.
        :rtype: PollState
        """
        from ..models import PollState

        return cast(
            PollState,
            await self(
                VotePollMethod,
                chat_id=chat_id,
                message_id=message_id,
                poll_id=poll_id,
                answer_ids=answer_ids,
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
        """Create group.

        :param title: The title value.
        :type title: str
        :param participant_ids: Identifiers of the participant objects.
        :type participant_ids: list[int] | None
        :param notify: Whether MAX should notify affected users.
        :type notify: bool
        :param chat_type: The chat type value.
        :type chat_type: str
        :param event: Incoming event to process.
        :type event: str
        :param typeof: Attachment class that determines the upload type.
        :type typeof: str
        :returns: The resulting tuple[Chat, Message] | tuple[None, None] value.
        :rtype: tuple[Chat, Message] | tuple[None, None]
        """
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
        """Invite users to group.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param user_ids: Identifiers of the users.
        :type user_ids: list[int]
        :param show_history: Show message history to new members.
        :type show_history: bool
        :returns: The resulting Chat | None value.
        :rtype: Chat | None
        """
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
        """Remove users from group.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param user_ids: Identifiers of the users.
        :type user_ids: list[int] | list[str]
        :param clean_msg_period: Cleanup period for messages from removed participants.
        :type clean_msg_period: int
        :returns: The resulting Chat | None value.
        :rtype: Chat | None
        """
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
        members_can_see_private_link: bool | None = None,
    ) -> Chat | None:
        """Change group settings.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param all_can_pin_message: All participants can pin messages.
        :type all_can_pin_message: bool | None
        :param only_owner_can_change_icon_title: The only owner can change icon title.
        :type only_owner_can_change_icon_title: bool | None
        :param only_admin_can_add_member: The only admin can add member.
        :type only_admin_can_add_member: bool | None
        :param only_admin_can_call: The only admin can call.
        :type only_admin_can_call: bool | None
        :param members_can_see_private_link: The members can see private link.
        :type members_can_see_private_link: bool | None
        :returns: The resulting Chat | None value.
        :rtype: Chat | None
        """
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
                members_can_see_private_link=members_can_see_private_link,
            ),
        )

    async def change_group_profile(
        self,
        chat_id: int,
        name: str | None = None,
        description: str | None = None,
    ) -> Chat | None:
        """Change group profile.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param name: The name of the chat.
        :type name: str | None
        :param description: The description of the chat.
        :type description: str | None
        :returns: The resulting Chat | None value.
        :rtype: Chat | None
        """
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
        """Join group.

        :param link: Invite group link.
        :type link: str
        :returns: The resulting Chat value.
        :rtype: Chat
        """
        from ..models import Chat

        return cast(
            Chat,
            await self(JoinGroupMethod, link=link),
        )

    async def join_channel(self, link: str) -> Chat:
        """Join channel.

        :param link: Invite channel link.
        :type link: str
        :returns: The resulting Chat value.
        :rtype: Chat
        """
        from ..models import Chat

        return cast(
            Chat,
            await self(JoinChannelMethod, link=link),
        )

    async def resolve_group_by_link(self, link: str) -> Chat | None:
        """Resolve group by link.

        :param link: Invite group link.
        :type link: str
        :returns: The resulting Chat | None value.
        :rtype: Chat | None
        """
        from ..models import Chat

        return cast(
            Chat | None,
            await self(ResolveGroupByLinkMethod, link=link),
        )

    async def revoke_invite_link(self, chat_id: int) -> Chat:
        """Revoke invite link.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :returns: The resulting Chat value.
        :rtype: Chat
        """
        from ..models import Chat

        return cast(
            Chat,
            await self(RevokeInviteLinkMethod, chat_id=chat_id),
        )

    async def get_chats(self, chat_ids: Iterable[int]) -> list[Chat]:
        """Retrieve chats.

        :param chat_ids: Identifiers of the chats.
        :type chat_ids: Iterable[int]
        :returns: The collection from gotten chats.
        :rtype: list[Chat]
        """
        from ..models import Chat

        return cast(
            list[Chat],
            await self(GetChatsMethod, chat_ids=chat_ids),
        )

    async def get_chat(self, chat_id: int) -> Chat:
        """Retrieve chat.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :returns: The resulting Chat value.
        :rtype: Chat
        :raises ValueError: If chat not found.
        """
        chats = await self.get_chats([chat_id])
        if not chats:
            raise ValueError("Chat not found")
        return chats[0]

    async def leave_group(self, chat_id: int) -> Message | None:
        """Leave group.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :returns: The resulting Message | None value.
        :rtype: Message | None
        """
        from ..models import Message

        return cast(
            Message | None,
            await self(
                LeaveGroupMethod,
                chat_id=chat_id,
            ),
        )

    async def leave_channel(self, chat_id: int) -> Message | None:
        """Leave channel.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :returns: The resulting Message | None value.
        :rtype: Message | None
        """
        from ..models import Message

        return cast(
            Message | None,
            await self(
                LeaveChannelMethod,
                chat_id=chat_id,
            ),
        )

    async def fetch_chats(self, marker: int | None = None) -> list[Chat]:
        """Fetch chats.

        :param marker: Pagination marker in milliseconds. If ``None``, the current time is used.
        :type marker: int | None
        :returns: The resulting Chats collection.
        :rtype: list[Chat]
        """
        from ..models import Chat

        return cast(
            list[Chat],
            await self(FetchChatsMethod, marker=marker),
        )

    async def get_join_requests(self, chat_id: int, count: int = 100) -> list[Member]:
        """Retrieve join requests.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param count: Maximum number of items to retrieve.
        :type count: int
        :returns: The resulting Members collection.
        :rtype: list[Member]
        """
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
        """Confirm join requests.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param user_ids: Identifiers of the users.
        :type user_ids: Iterable[int]
        :param show_history: Show message history to new members.
        :type show_history: bool
        :returns: The resulting Chat | None value.
        :rtype: Chat | None
        """
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
        """Confirm join request.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param user_id: Identifier of the user.
        :type user_id: int
        :param show_history: Show message history to new members.
        :type show_history: bool
        :returns: The resulting Chat | None value.
        :rtype: Chat | None
        """
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
        """Decline join requests.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param user_ids: Identifiers of the users.
        :type user_ids: Iterable[int]
        :returns: The resulting Chat | None value.
        :rtype: Chat | None
        """
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
        """Decline join request.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param user_id: Identifier of the user.
        :type user_id: int
        :returns: The resulting Chat | None value.
        :rtype: Chat | None
        """
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
        """Delete chat.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param last_event_time: The last event time value.
        :type last_event_time: int | None
        :param for_all: Delete only for the current account.
        :type for_all: bool
        """
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
        """Add admin.

        :param chat_id: Identifier of the chat.
        :type chat_id: int
        :param user_id: Identifier of the user.
        :type user_id: int
        :param permissions: Collection of permissions.
        :type permissions: Iterable[ChannelPermissions]
        """
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
        """Set 2fa.

        :param password: New 2FA password.
        :type password: str
        :param email: Email address for 2FA, if required.
        :type email: str | None
        :param hint: Password hint, if required.
        :type hint: str | None
        :param email_code_getter: Callable to get password, first argument is phone number.
        :type email_code_getter: Callable[[str], Coroutine[Any, Any, str]] | None
        :param two_factor_actions: Collection of two factor actions.
        :type two_factor_actions: list[TwoFactorAction] | None
        """
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
        """Remove 2fa.

        :param password: Account password.
        :type password: str
        :param two_factor_actions: Collection of two factor actions.
        :type two_factor_actions: list[TwoFactorAction] | None
        :param remove_2fa: The remove 2fa value.
        :type remove_2fa: bool
        """
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
        """Change password.

        :param password_old: The password old value.
        :type password_old: str
        :param password_new: The password new value.
        :type password_new: str
        :param hint: Password hint.
        :type hint: str | None
        :param two_factor_actions: Collection of two factor actions.
        :type two_factor_actions: list[TwoFactorAction] | None
        """
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
        """Check 2fa.

        :returns: True when the account has 2FA; otherwise False.
        :rtype: bool
        """
        return cast(
            bool,
            await self(
                Check2FaMethod,
            ),
        )

    async def approve_qr_login(self, qr_link: str) -> None:
        """Approve qr login.

        :param qr_link: Link to the authorization QR code.
        :type qr_link: str
        """
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
        """Change profile.

        :param first_name: The first name.
        :type first_name: str
        :param last_name: The last name.
        :type last_name: str | None
        :param description: The description.
        :type description: str | None
        :param photo: The photo data.
        :type photo: bytes | None
        :param file_name: The file name or photo file.
        :type file_name: str | None
        :param photo_token: The photo token value.
        :type photo_token: str | None
        :returns: The resulting Profile.
        :rtype: Profile
        """
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
        """Create folder.

        :param title: The title of folder.
        :type title: str
        :param chat_include: Collection of chat include.
        :type chat_include: list[int]
        :param filters: Collection of filters.
        :type filters: list[Any] | None
        :param folder_id: Identifier of the folder.
        :type folder_id: str | None
        :returns: The resulting FolderUpdate.
        :rtype: FolderUpdate
        """
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
        """Retrieve folders.

        :param folder_sync: Synchronization marker. Leave as ``0`` for the initial load..
        :type folder_sync: int
        :returns: The resulting FolderList.
        :rtype: FolderList
        """
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
        """Update folder.

        :param folder_id: Identifier of the folder.
        :type folder_id: str
        :param title: The title of folder.
        :type title: str
        :param chat_include: Collection of chat include.
        :type chat_include: list[int] | None
        :param filters: Collection of filters.
        :type filters: list[Any] | None
        :param options: Collection of options.
        :type options: list[Any] | None
        :returns: The resulting FolderUpdate.
        :rtype: FolderUpdate
        """
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
        folder_ids: list[str],
    ) -> FolderUpdate:
        """Delete folders.

        :param folder_ids: Identifiers of the folders.
        :type folder_ids: list[str]
        :returns: The resulting FolderUpdate.
        :rtype: FolderUpdate
        """
        from ..models import FolderUpdate

        return cast(
            FolderUpdate,
            await self(
                DeleteFoldersMethod,
                folder_ids=folder_ids,
            ),
        )

    async def delete_folder(self, folder_id: str) -> FolderUpdate:
        """Delete folder.

        :param folder_id: Identifier of the folder.
        :type folder_id: str
        :returns: The resulting FolderUpdate.
        :rtype: FolderUpdate
        """
        return await self.delete_folders(folder_ids=[folder_id])

    async def close_all_sessions(self) -> bool:
        """Close all sessions.

        :returns: ``True`` if the server accepted the request; otherwise ``False``.
        :rtype: bool
        """
        return cast(
            bool,
            await self(
                CloseAllSessionsMethod,
            ),
        )

    async def logout(self) -> None:
        """Logout."""
        return cast(None, await self(LogoutMethod))

    async def set_presence(self, online: bool) -> None:
        """Set presence.

        :param online: The online value.
        :type online: bool
        """
        return cast(
            None,
            await self(
                SetPresenceMethod,
                online=online,
            ),
        )

    async def change_profile_settings(self, privacy_settings: PrivacySettings) -> None:
        """Update the account privacy settings.

        :param privacy_settings: Privacy settings to apply to the account.

        :raises ValueError: If updating the privacy settings fails.

        :type privacy_settings: PrivacySettings
        """

        try:
            return cast(
                None,
                await self(
                    ChangeProfileSettingsMethod,
                    privacy_settings=privacy_settings,
                ),
            )
        except MapperApiError as e:
            raise ValueError("Change profile settings failed") from e

    async def get_members_by_ids(self, member_ids: list[int]) -> Sequence[Contact]:
        """Retrieve members by ids.

        :param member_ids: Identifiers of the members.
        :type member_ids: list[int]
        :returns: The Contacts collection.
        :rtype: Sequence[Contact]
        """
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
        """Retrieve member by id.

        :param member_id: Identifier of the member.
        :type member_id: int
        :returns: The resulting Contact | None.
        :rtype: Contact | None
        """
        contacts = await self.get_members_by_ids(member_ids=[member_id])
        return contacts[0] if contacts else None

    async def get_users(self, user_ids: list[int]) -> list[Contact]:
        """Retrieve users.

        :param user_ids: Identifiers of the users.
        :type user_ids: list[int]
        :returns: The resulting collection.
        :rtype: list[Contact]
        """
        from ..models import Contact

        user = cast(
            list[Contact],
            await self(
                GetUsersMethod,
                user_ids=user_ids,
            ),
        )
        return user

    async def get_user(self, user_id: int) -> Contact | None:
        """Retrieve user.

        :param user_id: Identifier of the user.
        :type user_id: int
        :returns: The resulting Contact | None.
        :rtype: Contact | None
        """
        user = await self.get_users(user_ids=[user_id])
        return user[0] if user else None

    async def search_by_phone(self, phone: str) -> Contact:
        """Search for by phone.

        :param phone: Phone number in the format accepted by MAX.
        :type phone: str
        :returns: The resulting Contact.
        :rtype: Contact
        """
        from ..models import Contact

        user = cast(
            Contact,
            await self(
                SearchByPhoneMethod,
                phone=phone,
            ),
        )
        return user

    async def get_sessions(self) -> list[Session]:
        """Retrieve sessions.

        :returns: The Sessions collection.
        :rtype: list[Session]
        """
        from ..models import Session

        return cast(list[Session], await self(GetSessionsMethod))

    async def get_chat_id(self, first_user_id: int, second_user_id: int) -> int:
        """Retrieve chat id.

        :param first_user_id: Identifier of the first user.
        :type first_user_id: int
        :param second_user_id: Identifier of the second user.
        :type second_user_id: int
        :returns: The resulting int value.
        :rtype: int
        """
        return cast(
            int,
            await self(
                GetChatIdMethod,
                first_user_id=first_user_id,
                second_user_id=second_user_id,
            ),
        )

    async def add_contact(self, contact_id: int) -> Contact:
        """Add contact.

        :param contact_id: Identifier of the contact.
        :type contact_id: int
        :returns: The resulting Contact.
        :rtype: Contact
        """
        from ..models import Contact

        return cast(
            Contact,
            await self(
                AddContactMethod,
                contact_id=contact_id,
            ),
        )

    async def remove_contact(self, contact_id: int) -> None:
        """Remove contact.

        :param contact_id: Identifier of the contact.
        :type contact_id: int
        """
        return cast(
            None,
            await self(
                RemoveContactMethod,
                contact_id=contact_id,
            ),
        )

    async def import_contacts(self, contacts: list[ContactInfo]) -> list[Contact]:
        """Import contacts.

        :param contacts: Collection of contacts.
        :type contacts: list[ContactInfo]
        :returns: The Contacts collection.
        :rtype: list[Contact]
        """
        from ..models import Contact

        return cast(
            list[Contact],
            await self(
                ImportContactsMethod,
                contacts=contacts,
            ),
        )
