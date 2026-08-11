# Finite-state machine

FSM stores a state and arbitrary data for a chat/user key. `Dispatcher` enables it by default with in-memory storage.

## Declare states

```python
from pyromax.fsm.state import State, StatesGroup


class Survey(StatesGroup):
    name = State()
    age = State()
```

## Use FSMContext

```python
from pyromax.filters import Command
from pyromax.fsm.context import FSMContext
from pyromax.models import Message


@dispatcher.message(Command("survey"))
async def begin(message: Message, state: FSMContext) -> None:
    await state.set_state(Survey.name)
    await message.reply("What is your name?")


@dispatcher.message(Survey.name)
async def receive_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Survey.age)
    await message.reply("How old are you?")


@dispatcher.message(Survey.age)
async def finish(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await message.reply(f"Saved: {data['name']}, {message.text}")
    await state.clear()
```

## Strategies

- `FSMStrategy.USER_IN_CHAT`: separate state for each user in each chat (default).
- `FSMStrategy.CHAT`: one state shared by the chat.
- `FSMStrategy.GLOBAL_USER`: one state per user across chats.

## Storage backends

```python
dispatcher = Dispatcher(storage=MemoryStorage())
```

`MemoryStorage` is suitable for development but loses data on restart. `RedisStorage` and `PyMongoStorage` provide persistent backends through optional dependencies. Pass a compatible client and optionally a `DefaultKeyBuilder`. Event isolation serializes updates that share an FSM key; choose an isolation implementation appropriate for the storage.

The dispatcher closes the configured FSM storage/isolation when polling ends.
