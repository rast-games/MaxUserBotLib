# Фильтры

Фильтр определяет, может ли обработчик принять событие. Он возвращает `True`, `False` или словарь, значения которого становятся доступными через DI.

## Встроенные фильтры

| Фильтр | Условие |
| --- | --- |
| `FromMeFilter` | Сообщение отправлено текущим аккаунтом |
| `ReplyToMessageFilter` | Ответ на сообщение |
| `MessageForwardFromFilter` | Пересланное сообщение |
| `MessageRemovedFilter` | Удалённое сообщение |
| `FromChatFilter` | Сообщение из выбранного чата |
| `HaveAttachFilter` | Есть вложения |
| `EmojiReactionAddFilter` | Реакция добавлена |
| `EmojiReactionRemoveFilter` | Реакция удалена |
| `Command` / `CommandStart` | Текстовая команда |

```python
from pyromax.filters import Command, CommandObject, FromChatFilter
from pyromax.models import Message


@dispatcher.message(Command("report"), FromChatFilter(12345))
async def report(message: Message, command: CommandObject) -> None:
    await message.reply(f"Аргументы: {command.args}")
```

## Magic filters

`F` экспортируется на верхнем уровне пакета и проверяет атрибуты моделей.

```python
from pyromax import F


@dispatcher.message(F.text.startswith("!"))
async def bang(message: Message) -> None:
    ...
```

## Пользовательский фильтр

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

Верните словарь наподобие `{ParsedValue: value}`, чтобы передать результат фильтра выбранному обработчику.
