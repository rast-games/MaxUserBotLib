from collections.abc import Awaitable, Callable
from typing import Any, cast

from ..core import MaxApi
from ..dispatcher.event import MaxObject
from ..dispatcher.middlewares.base import BaseMiddleware
from ..dispatcher.middlewares.event_resolvers import EventContext
from ..dispatcher.middlewares.user_context import EVENT_CONTEXT_KEY
from .context import FSMContext
from .storage.base import (
    DEFAULT_DESTINY,
    BaseEventIsolation,
    BaseStorage,
    StorageKey,
)
from .strategy import FSMStrategy, apply_strategy
from .state import RawState


class FSMContextMiddleware(BaseMiddleware):
    def __init__(
        self,
        storage: BaseStorage,
        events_isolation: BaseEventIsolation,
        strategy: FSMStrategy = FSMStrategy.USER_IN_CHAT,
    ):
        self.storage = storage
        self.strategy = strategy
        self.events_isolation = events_isolation

    async def __call__(
        self,
        handler: Callable[[MaxObject, dict[Any, Any]], Awaitable[Any]],
        event: MaxObject,
        data: dict[Any, Any],
    ) -> Any:
        max_api: MaxApi = cast(MaxApi, data[MaxApi])
        context = self.resolve_event_context(max_api, data)
        data[type(self.storage)] = self.storage
        if context:
            async with self.events_isolation.lock(key=context.key):
                data.update({FSMContext: context, RawState: await context.get_state()})
                return await handler(event, data)
        return await handler(event, data)

    def resolve_event_context(
        self,
        max_api: MaxApi,
        data: dict[Any, Any],
        destiny: str = DEFAULT_DESTINY,
    ) -> FSMContext | None:
        event_context: EventContext = cast(EventContext, data.get(EVENT_CONTEXT_KEY))
        return self.resolve_context(
            max_api=max_api,
            chat_id=event_context.chat_id,
            user_id=event_context.user_id,
            destiny=destiny,
        )

    def resolve_context(
        self,
        max_api: MaxApi,
        chat_id: int | None = None,
        user_id: int | None = None,
        destiny: str = DEFAULT_DESTINY,
    ) -> FSMContext | None:
        if chat_id is None:
            chat_id = user_id
        elif user_id is None and self.strategy in {FSMStrategy.CHAT}:
            user_id = chat_id

        if chat_id is not None and user_id is not None:
            chat_id, user_id = apply_strategy(
                chat_id=chat_id,
                user_id=user_id,
                strategy=self.strategy,
            )
            return self.get_context(
                max_api=max_api,
                chat_id=chat_id,
                user_id=user_id,
                destiny=destiny,
            )
        return None

    def get_context(
        self,
        max_api: MaxApi,
        chat_id: int,
        user_id: int,
        destiny: str = DEFAULT_DESTINY,
    ) -> FSMContext:
        max_api_id = max_api.id
        if max_api_id is None:
            max_api_id = 0
        return FSMContext(
            storage=self.storage,
            key=StorageKey(
                user_id=user_id,
                chat_id=chat_id,
                max_api_id=max_api_id,
                destiny=destiny,
            ),
        )

    async def close(self) -> None:
        await self.storage.close()
        await self.events_isolation.close()
