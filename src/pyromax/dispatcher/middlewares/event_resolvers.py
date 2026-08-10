from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from collections.abc import Callable

from ...models import Message, EmojiReaction

if TYPE_CHECKING:
    from ..event import MaxObject


@dataclass(frozen=True)
class EventContext:
    chat_id: int | None = None
    user_id: int | None = None


def resolve_message(m: Message) -> EventContext:
    return EventContext(chat_id=m.chat_id, user_id=m.sender_id)


def resolve_emoji_reaction(r: EmojiReaction) -> EventContext:
    return EventContext(chat_id=r.chat_id, user_id=None)


EVENT_STRUCTURE_RESOLVERS: dict[type[MaxObject], Callable[[Any], EventContext]] = {
    Message: resolve_message,
    EmojiReaction: resolve_emoji_reaction,
}
