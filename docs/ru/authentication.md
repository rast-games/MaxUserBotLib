# Авторизация

`MaxApi` создаёт транспорт, протокол и маппер, после чего передаёт авторизацию мапперу. Стек по умолчанию в 0.8: `websocket` + `EnvelopeProtocol` + `EnvelopeV11`, тип устройства — `WEB`.

## Авторизация по токену

```python
from pyromax import MaxApi

api = await MaxApi(
    token="YOUR_TOKEN",
    transport="websocket",
    device_type="WEB",
)
```

Используйте токен с тем же типом транспорта и устройства, для которого он был создан. Без токена маппер запускает интерактивный сценарий авторизации.

## Авторизация по QR-коду

Для стандартного web-стека не передавайте `token`. Если указан `url_callback`, маппер вызовет его с URL QR-кода; иначе стандартная реализация может использовать консоль.

```python
async def show_qr_url(url: str) -> None:
    print("Откройте или отрисуйте URL и отсканируйте его в MAX:", url)


api = await MaxApi(
    transport="websocket",
    device_type="WEB",
    url_callback=show_qr_url,
)
```

## Авторизация по телефону и SMS

Desktop-сценарий socket-envelope принимает параметры SMS через дополнительные аргументы маппера:

```python
async def get_sms_code(phone: str) -> int:
    print("Код запрошен для", phone)
    return int(input("Код из SMS: "))


api = await MaxApi(
    transport="socket_envelope",
    device_type="DESKTOP",
    sms_auth=True,
    phone_number="78005553535",
    code_getter=get_sms_code,
)
```

MAX ограничивает частоту отправки SMS. Не запрашивайте код многократно: сервер может временно ограничить аккаунт. 

[//]: # (Если маппер умеет переключаться на QR, передайте также QR callback.)

## Регистрация и middleware авторизации

`registration_config=RegistrationConfig(first_name=..., last_name=...)` задаёт данные профиля при регистрации.

### Жизненный цикл AuthFlow

Если `token` равен `None` и передан `auth_middleware_manager`, после создания выбранных mapper, protocol и transport клиент `MaxApi` создаёт `AuthFlow` и пропускает его через зарегистрированные auth middleware. Flow содержит:

- `token`: токен, найденный или установленный middleware; изначально `None`;
- `mapper`: активный экземпляр маппера;
- `protocol`: активный экземпляр протокола;
- `transport`: активный экземпляр транспорта.

Токен из возвращённого цепочкой flow передаётся в `mapper.initialize_client()`. Если в Pyromax сразу передать `token=...` в `MaxApi`, цепочка auth middleware не запускается.

### Создание и подключение менеджера

Создайте один `AuthMiddlewareManager`, зарегистрируйте middleware в порядке выполнения и передайте менеджер в `MaxApi`:

```python
from pyromax import MaxApi
from pyromax.auth import AuthMiddlewareManager

auth_manager = AuthMiddlewareManager()
auth_manager.register(FirstAuthMiddleware()) # или auth_manager(FirstAuthMiddleware())
auth_manager.register(SecondAuthMiddleware()) # или auth_manager(SecondAuthMiddleware())

api = await MaxApi(
    auth_middleware_manager=auth_manager,
    transport="websocket",
    protocol="EnvelopeProtocol",
    mapper="EnvelopeV11",
    device_type="WEB",
)
```

Вызов `auth_manager(MyMiddleware())` равнозначен `auth_manager.register(MyMiddleware())`; менеджер также можно использовать как декоратор.

### Типизация конкретного AuthFlow

Параметры generic-класса `AuthFlow` идут строго в таком порядке:

```python
AuthFlow[MapperType, ProtocolType, TransportType]
```

Для стандартного web-стека создайте type alias. Тогда middleware, IDE и type checker знают конкретные типы `event.mapper`, `event.protocol` и `event.transport`:

```python
import os
from collections.abc import Awaitable, Callable
from typing import Any

from pyromax.auth import AuthFlow, BaseAuthMiddleware
from pyromax.mapping import EnvelopeMapperV11
from pyromax.protocol.envelope import EnvelopeProtocol
from pyromax.transport import WebSocketTransport

WebAuthFlow = AuthFlow[
    EnvelopeMapperV11,
    EnvelopeProtocol,
    WebSocketTransport,
]


class FirstAuthMiddleware(BaseAuthMiddleware):
    async def __call__(
        self,
        handler: Callable[
            [WebAuthFlow, dict[type[Any] | str, Any]],
            Awaitable[Any],
        ],
        event: WebAuthFlow,
        data: dict[type[Any] | str, Any],
    ) -> WebAuthFlow:
        # Теперь атрибуты имеют конкретные статические типы.
        mapper: EnvelopeMapperV11 = event.mapper
        protocol: EnvelopeProtocol = event.protocol
        transport: WebSocketTransport = event.transport

        event.token = os.getenv("MAX_TOKEN")
        return await handler(event, data)
```

Цепочка вложена в порядке регистрации: первое middleware первым начинает выполнение до terminal handler и последним завершает его после handler. Для продолжения обязательно вызовите `await handler(event, data)`. Middleware может намеренно вернуть `AuthFlow` без вызова handler, чтобы остановить следующие auth middleware.

В словаре `data` также находятся активные client, mapper, protocol и transport под их конкретными runtime-типами. Это позволяет общим middleware получать backend-зависимости при необходимости.

## Совместимость backend

| Транспорт | Тип устройства | Протокол | Маппер |
| --- | --- | --- | --- |
| `websocket` | `WEB` | `EnvelopeProtocol` | `EnvelopeV11` |
| `socket_envelope` | `DESKTOP` | `EnvelopeProtocol` | `EnvelopeV11` |

[//]: # (Реестры расширяемы, но пользовательская комбинация должна реализовывать совместимые контракты транспорта, протокола и маппера. Неизвестное имя backend приводит к `RuntimeError` во время инициализации.)
