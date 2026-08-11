# Routing and handlers

## Router hierarchy

`Dispatcher` is the root router. Feature routers can contain their own handlers and child routers.

```python
from pyromax import Dispatcher, Router

dispatcher = Dispatcher()
admin = Router(name="admin")
dispatcher.include_router(admin)
```

`include_routers(*routers)` attaches several routers. A router cannot be attached twice, to itself, or in a cycle.

## Event observers

Every router exposes observers for:

- `message`, `edited_message`, `reply_to_message`, `forward_message`, and `message_removed`;
- `message_reaction`, `message_added_reaction`, and `message_deleted_reaction`;
- `error`.

Handlers are checked in registration order. The first matching handler consumes the event unless it explicitly calls `skip()`.

## Register a handler

```python
from pyromax.models import Message


@dispatcher.message(from_me=True)
async def echo(message: Message) -> None:
    await message.reply(message.text or "")
```

Message observers ignore messages sent by the current account unless `from_me=True` is passed.

## Typed dependency injection

Every handler parameter must be annotated. The resolver matches annotations against the data accumulated by the dispatcher, filters, middleware, FSM, and `MaxApi.workflow_data`.

```python
from pyromax import MaxApi
from pyromax.models import Message


@dispatcher.message()
async def inspect(message: Message, api: MaxApi) -> None:
    await api.set_presence(True)
```

Forward references are supported. Custom dependencies can be supplied globally:

```python
class Database:
    pass


api = await MaxApi(workflow_data={Database: Database()})


@dispatcher.message()
async def save(message: Message, database: Database) -> None:
    ...
```

Middleware is usually a better choice for request-scoped dependencies.
