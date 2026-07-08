from abc import ABC, abstractmethod
from typing import cast, TypeVar, Generic, Any

from ...payloads.shared import CamelCaseModel
from ......models import (Contact, Message, MessageLink, BaseMaxObject)
from ...payloads.models import (ContactMappingModel, MessageMappingModel, MessageLinkMappingModel)


TranslateObj = TypeVar('TranslateObj', bound=CamelCaseModel)

class BaseTranslateMappingModel(ABC, Generic[TranslateObj]):
    @staticmethod
    @abstractmethod
    def translate(mapping_model: TranslateObj) -> BaseMaxObject: pass


class TranslateContact(BaseTranslateMappingModel[ContactMappingModel]):
    @staticmethod
    def translate(contact: ContactMappingModel) -> Contact:
        return Contact(
            id=contact.id,
            name=contact.names[0].name if contact.names else '',
            description=contact.description,
            first_name=contact.names[0].first_name if contact.names else '',
            last_name=contact.names[0].last_name if contact.names else '',
            phone=str(contact.phone),
            avatar_url=contact.base_url,
            raw_avatar_url=contact.base_raw_url,
            photo_id=str(contact.photo_id),
            country=contact.country,
            account_status=contact.account_status,
            email=contact.email,
            registration_time=contact.registration_time,
        )

class TranslateMessage(BaseTranslateMappingModel[MessageMappingModel]):
    @staticmethod
    def translate(message: MessageMappingModel) -> Message:
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
                chat_id = -1
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
                        type=msg_link.type
                    )
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
        return translate_message(
            msg=message
        )


TRANSLATE_MAPPING_MODELS: dict[type[CamelCaseModel], type[BaseTranslateMappingModel[Any]]] = {
    ContactMappingModel: TranslateContact,
    MessageMappingModel: TranslateMessage
}



def translate_models(mapping_obj: CamelCaseModel) -> BaseMaxObject | CamelCaseModel:
    translate_model = TRANSLATE_MAPPING_MODELS.get(type(mapping_obj), None)
    if translate_model is None:
        return mapping_obj

    translated_obj = translate_model.translate(mapping_obj)

    return translated_obj
