# Машина состояний

FSM хранит состояние и произвольные данные для ключа чата/пользователя. По умолчанию Dispatcher включает FSM с хранилищем в памяти.

## Объявление состояний

```python
from pyromax.fsm.state import State, StatesGroup


class Survey(StatesGroup):
    name = State()
    age = State()
```

## Использование FSMContext

```python
from pyromax.filters import Command
from pyromax.fsm.context import FSMContext
from pyromax.models import Message


@dispatcher.message(Command("survey"))
async def begin(message: Message, state: FSMContext) -> None:
    await state.set_state(Survey.name)
    await message.reply("Как вас зовут?")


@dispatcher.message(Survey.name)
async def receive_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Survey.age)
    await message.reply("Сколько вам лет?")


@dispatcher.message(Survey.age)
async def finish(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await message.reply(f"Сохранено: {data['name']}, {message.text}")
    await state.clear()
```

## Стратегии

- `FSMStrategy.USER_IN_CHAT`: отдельное состояние пользователя в каждом чате (по умолчанию).
- `FSMStrategy.CHAT`: общее состояние всего чата.
- `FSMStrategy.GLOBAL_USER`: одно состояние пользователя во всех чатах.

## Хранилища

```python
dispatcher = Dispatcher(storage=MemoryStorage())
```

`MemoryStorage` подходит для разработки, но теряет данные после перезапуска. `RedisStorage` и `PyMongoStorage` используют дополнительные зависимости и сохраняют состояние постоянно. Передайте совместимый клиент и при необходимости `DefaultKeyBuilder`. Event isolation последовательно обрабатывает события с одинаковым FSM-ключом.

При завершении polling Dispatcher закрывает FSM storage и isolation.
