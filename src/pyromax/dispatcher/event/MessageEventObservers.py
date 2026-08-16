from collections.abc import Callable
from typing import Any

from .StandardMaxEventObserver import StandardMaxEventObserver
from ...models import Message
from ...filters import (
    Filter,
    FromMeFilter,
    MessageForwardFromFilter,
    ReplyToMessageFilter,
    MessageRemovedFilter,
)
from .Handler import FilterObject


class MessageEventObserver(StandardMaxEventObserver[Message]):
    """Observe regular message events and register message handlers."""

    def __call__(
        self,
        *filters: Filter,
        pattern: Callable[[Message], bool] | None = None,
        soft_propagate: bool = False,
        from_me: bool = False,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a message handler decorator.

        :param filters: Additional filters applied to the handler.
        :type filters: Filter
        :param pattern: Optional message predicate.
        :type pattern: Callable[[Message], bool] | None
        :param from_me: If True, allow messages from the current user.
        :type from_me: bool

        :returns: The resulting Callable[[Callable[..., Any]], None] value.
        :rtype: Callable[[Callable[..., Any]], None]
        """
        filters_list = []
        filters_list += list(filters)
        if not from_me:
            filters_list.append(~FromMeFilter())

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            """Decorator.

            :param func: Callable to invoke.
            :type func: Callable[..., Any]
            """
            self.register(
                func,
                *filters_list,
                pattern=pattern,
                soft_propagate=soft_propagate,
            )
            return func

        return decorator

    async def is_my_update(self, update: Message) -> bool:
        """Return whether my update.

        :param update: Incoming update to process.
        :type update: Message
        :returns: True when the requested condition is satisfied; otherwise False.
        :rtype: bool
        """
        return await super().is_my_update(update) and update.status == self.event_name


class MessageForwardEventObserver(MessageEventObserver):
    """Observe forwarded messages."""

    async def is_my_update(self, update: Message) -> bool:
        """Return whether my update.

        :param update: Incoming update to process.
        :type update: Message
        :returns: True when the requested condition is satisfied; otherwise False.
        :rtype: bool
        """
        forward_filter = FilterObject(MessageForwardFromFilter())
        return await StandardMaxEventObserver.is_my_update(self, update) and bool(
            await forward_filter(update, data={Message: update})
        )


class ReplyToMessageEventObserver(MessageEventObserver):
    """Observe reply messages."""

    async def is_my_update(self, update: Message) -> bool:
        """Return whether my update.

        :param update: Incoming update to process.
        :type update: Message
        :returns: True when the requested condition is satisfied; otherwise False.
        :rtype: bool
        """
        reply_filter = FilterObject(ReplyToMessageFilter())
        return await StandardMaxEventObserver.is_my_update(self, update) and bool(
            await reply_filter(update, data={Message: update})
        )


class RemovedMessageEventObserver(MessageEventObserver):
    """Observe removed messages."""

    async def is_my_update(self, update: Message) -> bool:
        """Return whether my update.

        :param update: Incoming update to process.
        :type update: Message
        :returns: True when the requested condition is satisfied; otherwise False.
        :rtype: bool
        """
        removed_filter = FilterObject(MessageRemovedFilter())
        return await StandardMaxEventObserver.is_my_update(self, update) and bool(
            await removed_filter(update, data={Message: update})
        )
