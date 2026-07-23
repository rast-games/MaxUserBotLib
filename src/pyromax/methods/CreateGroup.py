from typing import Union, cast

from .Base import BaseMaxApiMethod
from ..models import Chat


class CreateGroupMethod(BaseMaxApiMethod[Union[Chat, None]]):
    async def __call__(
        self,
        title: str,
        participant_ids: list[int] | None = None,
        notify: bool = True,
        chat_type: str = "CHAT",
        event: str = "new",
        typeof: str = "CONTROL",
    ) -> Chat | None:
        if not self._max_api:
            raise RuntimeError("CreateGroup method not bound to MaxApi instance")

        return cast(
            Chat | None,
            await self._max_api.mapper.call_method(
                type(self),
                title=title,
                participant_ids=participant_ids,
                notify=notify,
                chat_type=chat_type,
                event=event,
                typeof=typeof,
            ),
        )
