from typing import cast

from .Base import BaseMaxApiMethod
from ..models.Poll import Poll


class CreatePollMethod(BaseMaxApiMethod[Poll]):
    async def __call__(
        self,
        poll: Poll,
    ) -> Poll:
        if not self._max_api:
            raise RuntimeError("CreatePoll method not bound to MaxApi instance")

        return cast(
            Poll,
            await self._max_api.mapper.call_method(
                type(self),
                poll=poll,
            ),
        )
