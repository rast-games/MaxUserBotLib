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
