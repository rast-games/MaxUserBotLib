from typing import cast

from .Base import BaseMaxApiMethod
from ..models.Poll import Poll


class CreatePollMethod(BaseMaxApiMethod[Poll]):
    async def __call__(
        self,
        poll: Poll,
    ) -> Poll:
        """Execute the create poll MAX API method.

        :param poll: Poll instance to process.
        :type poll: Poll
        :returns: The resulting Poll value.
        :rtype: Poll
        :raises RuntimeError: If createPoll method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("CreatePoll method not bound to MaxApi instance")

        return cast(
            Poll,
            await self._max_api.mapper.call_method(
                type(self),
                poll=poll,
            ),
        )
