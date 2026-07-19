from .base import BaseMethod, Envelope, Cmd, Opcode, VERSION
from ...payloads.requests import SendMessageRequest, GetMessagesRequest
from ...translate.FromDTO import reverse_translate_message
from ...payloads.models import MessageMappingModel, MessageLinkMappingModel


class SendMessageMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.SEND_MESSAGE
        request.cmd = Cmd.REQUEST
        request.ver = VERSION

        main_link = self.args.get('link')
        request.payload = SendMessageRequest(
            chat_id=self.args['chat_id'],
            message=MessageMappingModel(
                text=self.args.get('text'),
                cid=self.args['cid'],
                attaches=self.args['attaches'],
                elements=self.args['elements'] if self.args['text'] and self.args['elements'] else None,
                link=MessageLinkMappingModel(
                    type=main_link.type,
                    message_id=int(main_link.message_id),
                    chat_id=main_link.chat_id,
                    message=reverse_translate_message(main_link.message),
                ) if main_link else None,
            ),
        ).model_dump(by_alias=True, exclude_none=True)
        return request


class GetMessagesMethod(BaseMethod):
    async def __call__(self, request: Envelope) -> Envelope:
        request.opcode = Opcode.GET_MESSAGES
        request.cmd = Cmd.REQUEST
        request.ver = VERSION
        request.payload = GetMessagesRequest(
            message_ids=self.args['message_ids'],
            chat_id=self.args['chat_id'],
        ).model_dump(by_alias=True, exclude_none=True)
        return request


__all__ = [
    'SendMessageMethod',
    'GetMessagesMethod'
]