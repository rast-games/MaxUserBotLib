# Filters

Filters decide whether a handler can process an event. They may return `True`, `False`, or a dictionary whose values become injectable handler dependencies.

## Built-in filters

| Filter | Matches |
| --- | --- |
| `FromMeFilter` | Messages sent by the authenticated account |
| `ReplyToMessageFilter` | Reply messages |
| `MessageForwardFromFilter` | Forwarded messages |
| `MessageRemovedFilter` | Removed messages |
| `FromChatFilter` | Messages from selected chat IDs |
| `HaveAttachFilter` | Messages containing attachments |
| `EmojiReactionAddFilter` | Added reactions |
| `EmojiReactionRemoveFilter` | Removed reactions |
| `Command` / `CommandStart` | Parsed text commands |

```python
from pyromax.filters import Command, CommandObject, FromChatFilter
from pyromax.models import Message


@dispatcher.message(Command("report"), FromChatFilter(12345))
async def report(message: Message, command: CommandObject) -> None:
    await message.reply(f"Arguments: {command.args}")
```

## Magic filters

`F` is exported at package level and can inspect model attributes.

```python
from pyromax import F


@dispatcher.message(F.text.startswith("!"))
async def bang(message: Message) -> None:
    ...
```

## Custom filter

```python
from typing import Any

from pyromax.filters import Filter
from pyromax.models import Message


class Contains(Filter):
    def __init__(self, needle: str) -> None:
        super().__init__()
        self.needle = needle

    @property
    def work_with(self) -> tuple[type[Message], ...]:
        return (Message,)

    async def _check(self, message: Message) -> bool | dict[str, Any]:
        return bool(message.text and self.needle in message.text)
```

Return a dictionary such as `{ParsedValue: value}` to inject a filter result into the selected handler.
