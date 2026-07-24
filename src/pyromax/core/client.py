from __future__ import annotations
import asyncio
import logging
from typing import Any, TYPE_CHECKING, AsyncGenerator, cast, Literal, overload
from collections.abc import Sequence, Callable, Iterable

from ..mixins import AsyncInitializerMixin
from ..methods import (
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
)
from ..exceptions import SendMessageError

if TYPE_CHECKING:
    from ..dispatcher.event import Update, MaxObject
    from ..protocol import Response
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
    )

from .context import *

if TYPE_CHECKING:
    from ..protocol import BaseMaxProtocol
    from ..transport import BaseTransport
    from ..mapping import BaseMapper
    from ..models import Contact


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
        )

        await self.mapper.initialize_client(
            token=token,
            device_type=device_type,
            password=password,
            user_agent_params=user_agent_params,
            **kwargs,
        )

    def __init__(
        self,
        device_type: str = "WEB",
        password: str | None = None,
        transport: str | BaseTransport | None = None,
        protocol: str | BaseMaxProtocol[Any, Any] | None = None,
        mapper: BaseMapper[Any, Any] | None = None,
        transport_options: dict[str, Any] | None = None,
        token: str | None = None,
        logger: logging.Logger | None = None,
        workflow_data: dict[Any, Any] | None = None,
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
        self.messages: dict[int, list[Message]]

        self.__logger: logging.Logger | None = logger
        self.workflow_data = workflow_data

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

    async def get_member_by_id(self, member_id: int) -> Sequence[Contact]:
        from ..models import Contact

        contacts = cast(
            Sequence[Contact],
            await self(
                GetMemberByIdMethod,
                member_id=member_id,
            ),
        )
        return contacts
        # return await self.mapper.get_member_by_id(member_id)

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
        user_ids: list[int] | list[str],
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
