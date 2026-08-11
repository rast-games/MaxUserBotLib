# Authentication

`MaxApi` initializes the transport, protocol, and mapper before delegating authentication to the mapper. In 0.8, the default stack is `websocket` + `EnvelopeProtocol` + `EnvelopeV11` with device type `WEB`.

## Token authentication

```python
from pyromax import MaxApi

api = await MaxApi(
    token="YOUR_TOKEN",
    transport="websocket",
    device_type="WEB",
)
```

Use a token with the same kind of transport/device context that created it. If no token is supplied, the mapper begins an interactive authentication flow.

## QR authentication

For the default web stack, omit `token`. If the mapper receives a `url_callback`, it calls it with the QR URL; otherwise the default authentication implementation may use the console.

```python
async def show_qr_url(url: str) -> None:
    print("Open or render this URL and scan it in MAX:", url)


api = await MaxApi(
    transport="websocket",
    device_type="WEB",
    url_callback=show_qr_url,
)
```

## Phone/SMS authentication

The desktop socket-envelope scenario accepts phone/SMS options through mapper keyword arguments:

```python
async def get_sms_code(phone: str) -> int:
    print("Code requested for", phone)
    return int(input("SMS code: "))


api = await MaxApi(
    transport="socket_envelope",
    device_type="DESKTOP",
    sms_auth=True,
    phone_number="78005553535",
    code_getter=get_sms_code,
)
```

SMS delivery is rate-limited by MAX. Do not repeatedly request codes; the server may temporarily restrict the account. 

[//]: # (Provide a QR callback. if the selected mapper can fall back to QR authentication.)


## Registration and authentication middleware

`registration_config=RegistrationConfig(first_name=..., last_name=...)` supplies profile data when registration is required.

### AuthFlow lifecycle

When `token` is `None` and `auth_middleware_manager` is provided, `MaxApi` creates an `AuthFlow` after constructing the selected mapper, protocol, and transport. It then passes that flow through every registered auth middleware. The flow contains:

- `token`: a token supplied or discovered by middleware, initially `None`;
- `mapper`: the active mapper instance;
- `protocol`: the active protocol instance;
- `transport`: the active transport instance.

The flow returned by the middleware chain supplies the token to `mapper.initialize_client()`. Passing `token=...` directly to `MaxApi` skips the auth middleware chain.

### Create and connect the manager

Create one `AuthMiddlewareManager`, register middleware in execution order, and pass the manager to `MaxApi`:

```python
from pyromax import MaxApi
from pyromax.auth import AuthMiddlewareManager

auth_manager = AuthMiddlewareManager()
auth_manager.register(FirstAuthMiddleware()) # or auth_manager(FirstAuthMiddleware())
auth_manager.register(SecondAuthMiddleware()) # or auth_manager(SecondAuthMiddleware())

api = await MaxApi(
    auth_middleware_manager=auth_manager,
    transport="websocket",
    protocol="EnvelopeProtocol",
    mapper="EnvelopeV11",
    device_type="WEB",
)
```

`auth_manager(MyMiddleware())` is equivalent to `auth_manager.register(MyMiddleware())` and can also be used as a decorator.

### Type a concrete AuthFlow

`AuthFlow` is generic in this exact order:

```python
AuthFlow[MapperType, ProtocolType, TransportType]
```

For the default web stack, define an alias so the middleware, IDE, and type checker know the concrete types of `event.mapper`, `event.protocol`, and `event.transport`:

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
        # These attributes now have concrete static types.
        mapper: EnvelopeMapperV11 = event.mapper
        protocol: EnvelopeProtocol = event.protocol
        transport: WebSocketTransport = event.transport

        event.token = os.getenv("MAX_TOKEN")
        return await handler(event, data)
```

The middleware chain is nested in registration order: the first registered middleware runs first before the terminal handler and finishes last after it. Call `await handler(event, data)` to continue the chain. A middleware may deliberately return an `AuthFlow` without calling the handler to stop further auth middleware.

The `data` dictionary also contains the active client, mapper, protocol, and transport under their concrete runtime types. This allows shared middleware utilities to resolve backend-specific objects when necessary.

## Backend compatibility

| Transport | Device type | Protocol | Mapper |
| --- | --- | --- | --- |
| `websocket` | `WEB` | `EnvelopeProtocol` | `EnvelopeV11` |
| `socket_envelope` | `DESKTOP` | `EnvelopeProtocol` | `EnvelopeV11` |

[//]: # (The registries are extensible, but a custom combination must implement compatible transport, protocol, and mapper contracts. Unsupported registry names raise `RuntimeError` during initialization.)
