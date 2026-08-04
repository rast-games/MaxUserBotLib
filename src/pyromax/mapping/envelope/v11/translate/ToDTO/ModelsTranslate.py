from abc import ABC, abstractmethod
from typing import cast, TypeVar, Generic, Any, TYPE_CHECKING, Literal

from ...payloads.responses import CreateGroupResponse
from ...payloads.shared import CamelCaseModel
from ......models import (
    Contact,
    Message,
    MessageLink,
    BaseMaxObject,
    EmojiReaction,
    ReadState,
    Chat,
    Name,
    Profile,
    Presence,
    Member,
    Folder,
    FolderUpdate,
    FolderList,
    Session,
)
from ...payloads.models import (
    ContactMappingModel,
    MessageMappingModel,
    ReadStateMappingModel,
    MessageLinkMappingModel,
    ReactionInfoMappingModel,
    ChatMappingModel,
    NameMappingModel,
    ProfileMappingModel,
    PresenceMappingModel,
    MemberMappingModel,
    FolderMappingModel,
    FolderUpdateMappingModel,
    FolderListMappingModel,
    SessionMappingModel,
)

TranslateObj = TypeVar("TranslateObj", bound=CamelCaseModel)


class BaseTranslateMappingModel(ABC, Generic[TranslateObj]):

    if TYPE_CHECKING:

        @staticmethod
        @abstractmethod
        def translate(*args: Any, **kwargs: Any) -> BaseMaxObject:
            pass

    else:

        @staticmethod
        @abstractmethod
        def translate(
            mapping_model: TranslateObj, *args: Any, **kwargs: Any
        ) -> BaseMaxObject:
            pass


class TranslateName(BaseTranslateMappingModel[NameMappingModel]):
    @staticmethod
    def translate(
        mapping_model: NameMappingModel,
    ) -> Name:
        return Name(
            name=mapping_model.name,
            first_name=mapping_model.first_name,
            last_name=mapping_model.last_name,
            type=mapping_model.type,
        )


class TranslateContact(BaseTranslateMappingModel[ContactMappingModel]):
    @staticmethod
    def translate(contact: ContactMappingModel) -> Contact:
        return Contact(
            id=contact.id,
            names=[TranslateName.translate(name) for name in contact.names],
            description=contact.description,
            first_name=contact.names[0].first_name if contact.names else "",
            last_name=contact.names[0].last_name if contact.names else "",
            phone=str(contact.phone),
            avatar_url=contact.base_url,
            raw_avatar_url=contact.base_raw_url,
            photo_id=str(contact.photo_id),
            country=contact.country,
            account_status=contact.account_status,
            email=contact.email,
            registration_time=contact.registration_time,
            update_time=contact.update_time,
            options=contact.options,
            status=contact.status,
            gender=contact.gender,
            link=contact.link,
            web_app=contact.web_app,
            menu_button=contact.menu_button,
        )


class TranslateProfile(BaseTranslateMappingModel[ProfileMappingModel]):
    @staticmethod
    def translate(profile: ProfileMappingModel) -> Profile:
        profile_options = []
        for option in profile.profile_options:
            if isinstance(option, int):
                profile_options.append(option)
            elif isinstance(option, str) and option.isdigit():
                profile_options.append(int(option))
        return Profile(
            contact=TranslateContact.translate(profile.contact),
            profile_options=profile_options,
        )


class TranslatePresence(BaseTranslateMappingModel[PresenceMappingModel]):
    @staticmethod
    def translate(presence: PresenceMappingModel) -> Presence:
        return Presence(
            seen=presence.seen,
            status=presence.status,
        )


class TranslateMember(BaseTranslateMappingModel[MemberMappingModel]):
    @staticmethod
    def translate(member: MemberMappingModel) -> Member:
        return Member(
            presence=TranslatePresence.translate(member.presence),
            contact=TranslateContact.translate(member.contact),
        )


class TranslateMessage(BaseTranslateMappingModel[MessageMappingModel]):
    @staticmethod
    def translate(message: MessageMappingModel, fallback_chat_id: int = -1) -> Message:

        def translate_message(msg: MessageMappingModel) -> Message:
            msg_id = msg.id
            # if message.id is None:
            #     msg_id = 0
            # else:
            #     msg_id = int(msg_id) if type(msg_id) is str and msg_id.isdigit() or type(msg_id) is int else 0

            msg_link = msg.link

            if type(msg_id) is str:
                msg_id = int(msg_id) if msg_id.isdigit() else 0
            elif msg_id is None:
                msg_id = -1
            else:
                msg_id = msg_id

            if msg.chat_id is None:
                chat_id = fallback_chat_id
            else:
                chat_id = msg.chat_id

            if msg.time is None:
                msg_time = -1
            else:
                msg_time = msg.time
            if msg_link is not None and msg_link.message is not None:
                return Message(
                    message_id=cast(int, msg_id),
                    type=msg.type,
                    chat_id=chat_id,
                    cid=msg.cid,
                    time=msg_time,
                    text=msg.text,
                    status=msg.status,
                    elements=msg.elements,
                    sender_id=msg.sender,
                    attaches=msg.attaches,
                    link=MessageLink(
                        message=translate_message(msg=msg_link.message),
                        message_id=msg_link.message_id,
                        type=msg_link.type,
                    ),
                )

            return Message(
                message_id=cast(int, msg_id),
                type=msg.type,
                chat_id=chat_id,
                cid=msg.cid,
                time=msg_time,
                text=msg.text,
                status=msg.status,
                elements=msg.elements,
                sender_id=msg.sender,
                attaches=msg.attaches,
            )

        return translate_message(msg=message)


class TranslateReactionInfo(BaseTranslateMappingModel[ReactionInfoMappingModel]):

    @staticmethod
    def translate(
        reaction: ReactionInfoMappingModel,
        chat_id: int,
        message_id: int | str,
        status: str = "ADD",
    ) -> EmojiReaction:
        from ......models.EmojiReaction import Counters

        return EmojiReaction(
            chat_id=chat_id,
            message_id=message_id,
            counters=cast(list[Counters] | None, reaction.counters),
            total_count=reaction.total_count,
            your_reaction=reaction.your_reaction,
            status=cast(Literal["ADD", "REMOVE"], status),
        )


class TranslateReadState(BaseTranslateMappingModel[ReadStateMappingModel]):
    @staticmethod
    def translate(
        read_state: ReadStateMappingModel,
        chat_id: int,
        message_id: int | str,
    ) -> ReadState:
        return ReadState(
            chat_id=chat_id,
            message_id=message_id,
            mark=read_state.mark,
            unread=read_state.unread,
        )


class TranslateChat(BaseTranslateMappingModel[ChatMappingModel]):
    @staticmethod
    def translate(chat: ChatMappingModel) -> Chat:
        return Chat(
            id=chat.id,
            type=chat.type,
            status=chat.status,
            owner=chat.owner,
            participants=chat.participants,
            title=chat.title,
            base_raw_icon_url=chat.base_raw_icon_url,
            base_icon_url=chat.base_icon_url,
            last_message=(
                TranslateMessage.translate(
                    message=chat.last_message, fallback_chat_id=chat.id
                )
                if chat.last_message
                else None
            ),
            last_event_time=chat.last_event_time,
            last_delayed_update_time=chat.last_delayed_update_time,
            last_fire_delayed_error_time=chat.last_fire_delayed_error_time,
            created=chat.created,
            new_messages=chat.new_messages,
            link=chat.link,
            access=chat.access,
            restrictions=chat.restrictions,
            pinned_message=(
                TranslateMessage.translate(
                    message=chat.pinned_message, fallback_chat_id=chat.id
                )
                if chat.pinned_message
                else None
            ),
            participants_count=chat.participants_count,
            description=chat.description,
            options=chat.options,
            join_time=chat.join_time,
            invited_by=chat.invited_by,
            modified=chat.modified,
            messages_count=chat.messages_count,
            has_bots=chat.has_bots,
            prev_message_id=chat.prev_message_id,
            admin_participants=chat.admin_participants,
            admins=chat.admins,
            cid=chat.cid,
        )


class TranslateFolder(BaseTranslateMappingModel[FolderMappingModel]):
    @staticmethod
    def translate(folder: FolderMappingModel) -> Folder:
        return Folder(
            source_id=folder.source_id,
            include=folder.include,
            options=folder.options,
            update_time=folder.update_time,
            id=folder.id,
            filters=folder.filters,
            title=folder.title,
        )


class TranslateFolderUpdate(BaseTranslateMappingModel[FolderUpdateMappingModel]):

    @staticmethod
    def translate(folder_update: FolderUpdateMappingModel) -> FolderUpdate:
        return FolderUpdate(
            folder_sync=folder_update.folder_sync,
            folders_order=folder_update.folders_order,
            folder=(
                TranslateFolder.translate(folder=folder_update.folder)
                if folder_update.folder is not None
                else folder_update.folder
            ),
        )


class TranslateFolderList(BaseTranslateMappingModel[FolderListMappingModel]):

    @staticmethod
    def translate(folder_list: FolderListMappingModel) -> FolderList:
        return FolderList(
            folder_sync=folder_list.folder_sync,
            folders_order=folder_list.folders_order,
            all_filter_exclude_folders=folder_list.all_filter_exclude_folders,
            folders=[
                TranslateFolder.translate(folder) for folder in folder_list.folders
            ],
        )


class TranslateSession(BaseTranslateMappingModel[SessionMappingModel]):
    @staticmethod
    def translate(session: SessionMappingModel) -> Session:
        if ", IP" in session.location:
            location, ip = tuple(
                map(
                    str.strip,
                    session.location.split(", IP"),
                )
            )
        else:
            location = session.location
            ip = None
        return Session(
            id=session.id,
            device_id=session.device_id,
            current=session.current,
            user_agent=session.user_agent,
            app_version=session.app_version,
            device_name=session.client or session.device_name,
            device_type=session.device_type,
            platform=session.platform,
            ip=ip,
            location=location,
            created=session.created,
            updated=session.updated,
            last_activity=session.last_activity,
            options=session.options,
            info=session.info,
            time=session.time,
        )


TRANSLATE_MAPPING_MODELS: dict[
    type[CamelCaseModel], type[BaseTranslateMappingModel[Any]]
] = {
    ContactMappingModel: TranslateContact,
    MessageMappingModel: TranslateMessage,
    ReactionInfoMappingModel: TranslateReactionInfo,
    ReadStateMappingModel: TranslateReadState,
    ChatMappingModel: TranslateChat,
    NameMappingModel: TranslateName,
    ProfileMappingModel: TranslateProfile,
    PresenceMappingModel: TranslatePresence,
    MemberMappingModel: TranslateMember,
    FolderMappingModel: TranslateFolder,
    FolderUpdateMappingModel: TranslateFolderUpdate,
    FolderListMappingModel: TranslateFolderList,
    SessionMappingModel: TranslateSession,
}


def translate_models(
    mapping_obj: CamelCaseModel, *args: Any, **kwargs: Any
) -> BaseMaxObject | CamelCaseModel:
    translate_model = TRANSLATE_MAPPING_MODELS.get(type(mapping_obj), None)
    if translate_model is None:
        return mapping_obj

    translated_obj = translate_model.translate(mapping_obj, *args, **kwargs)

    return translated_obj
