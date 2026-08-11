# Middleware и внедрение зависимостей

Middleware оборачивает обработку события и получает следующий handler, текущее событие и изменяемый словарь данных.

```python
from collections.abc import Awaitable, Callable
from typing import Any

from pyromax import Dispatcher
from pyromax.dispatcher.middlewares.base import BaseMiddleware
from pyromax.dispatcher.event import MaxObject


class RequestContext:
    pass


class ContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[MaxObject, dict[type[Any] | str, Any]], Awaitable[Any]],
        event: MaxObject,
        data: dict[type[Any] | str, Any],
    ) -> Any:
        data[RequestContext] = RequestContext()
        return await handler(event, data)


dispatcher = Dispatcher()
dispatcher.update.outer_middleware(ContextMiddleware())
```

После этого объект доступен по аннотации:

```python
@dispatcher.message()
async def handle(context: RequestContext) -> None:
    ...
```

## Внешние middleware и middleware observer

Внешнее middleware Dispatcher окружает разрешение update и все routed handlers. Middleware observer относится к конкретному типу события. Цепочка входит в middleware в порядке регистрации, а выходит в обратном порядке.

## Встроенные middleware Dispatcher

По умолчанию устанавливаются:

- `ErrorsMiddleware` для передачи ошибок;
- `UserContextMiddleware` для контекста пользователя и чата;
- `FSMContextMiddleware`, если не задано `disable_fsm=True`.

Всегда вызывайте и возвращайте `await handler(event, data)`, если middleware не должно намеренно остановить распространение события.
