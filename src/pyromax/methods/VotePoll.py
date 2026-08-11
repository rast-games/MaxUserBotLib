from typing import cast

from .Base import BaseMaxApiMethod
from ..models import PollState


class VotePollMethod(BaseMaxApiMethod[PollState]):
    async def __call__(
        self,
        chat_id: int,
        message_id: int | str,
        poll_id: int,
        answer_ids: list[int],
    ) -> PollState:
        """Execute the vote poll MAX API method.

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
        :raises RuntimeError: If votePoll method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("VotePoll method not bound to MaxApi instance")

        return cast(
            PollState,
            await self._max_api.mapper.call_method(
                type(self),
                chat_id=chat_id,
                message_id=message_id,
                poll_id=poll_id,
                answer_ids=answer_ids,
            ),
        )
