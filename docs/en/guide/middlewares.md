# Middleware and dependency injection

Middleware wraps event processing. It receives the next handler, the current event, and a mutable data dictionary.

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

The injected object is then available by annotation:

```python
@dispatcher.message()
async def handle(context: RequestContext) -> None:
    ...
```

## Outer and observer middleware

Dispatcher outer middleware surrounds update resolution and all routed handlers. Observer middleware belongs to an event observer and only wraps handlers registered for that event. Middleware is executed in registration order and unwinds in reverse order around the handler.

## Built-in dispatcher middleware

By default `Dispatcher` installs:

- `ErrorsMiddleware` for error propagation;
- `UserContextMiddleware` for user/chat context;
- `FSMContextMiddleware`, unless `disable_fsm=True`.

Always call and return `await handler(event, data)` unless the middleware intentionally stops propagation.
