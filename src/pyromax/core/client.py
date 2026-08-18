from __future__ import annotations
import asyncio
import logging
from typing import (
    TYPE_CHECKING,
    AsyncGenerator,
)
from collections.abc import Callable
from typing import Any, cast

from ..config import ExtraConfig, from_config_to_registry
from ..mixins import AsyncInitializerMixin
from ..utils import hide_func_call

if TYPE_CHECKING:
    from ..dispatcher.event import MaxObject
    from ..protocol import Response, BaseMaxProtocol
    from ..transport import BaseTransport
    from ..encoding import BaseEncoding
    from ..mapping import BaseMapper
    from ..methods import BaseMaxApiMethod
    from ..models import (
        Chat,
        Profile,
        Name,
        Contact,
        RegistrationConfig,
        TransportRegistry,
        EncodingRegistry,
        ProtocolRegistry,
        MapperRegistry,
        DeviceType,
    )
    from ..auth import AuthMiddlewareManager

from .context import *
from .CoreMixins import FullMixin, AsyncConstructorProtocolMeta
from ..exceptions import (
    MapperTransportError,
    BaseMaxApiMethodError,
    BaseMapperError,
    MapperApiError,
)


class MaxApi(AsyncInitializerMixin, FullMixin, metaclass=AsyncConstructorProtocolMeta):
    """Asynchronous client for MAX Messenger.

    The client initializes a transport, protocol, and mapper from the
    project registry. Initialization is asynchronous and requires the
    selected backend names to be available in the corresponding registries.

    :raises RuntimeError: If a transport, protocol, or mapper name is not supported.
    """

    async def _async_init(
        self,
        device_type: DeviceType | None = None,  # default "WEB"
        password: str | None = None,
        token: str | None = None,
        phone: str | None = None,
        transport: TransportRegistry | None = None,
        encoding: EncodingRegistry | None = None,
        protocol: ProtocolRegistry | None = None,
        mapper: MapperRegistry | None = None,
        workflow_data: dict[Any, Any] | None = None,
        auth_middleware_manager: AuthMiddlewareManager | None = None,
        extra_config: ExtraConfig | None = None,
        **kwargs: Any,
    ) -> None:
        """Asynchronously initialize transport, protocol, and mapper.

        :param device_type: Device type reported to the API.
        :type device_type: str
        :param password: Optional account password.
        :type password: str | None
        :param token: Optional auth token.
        :type token: str | None
        :param transport: Transport backend name.
        :type transport: str
        :param protocol: Protocol backend name.
        :type protocol: str
        :param mapper: Mapper backend name.
        :type mapper: str
        :param transport_options: Keyword arguments passed to the transport constructor.
        :type transport_options: dict[str, Any] | None
        :param kwargs: Extra keyword arguments passed to mapper initialization.
        :type kwargs: Any

        :param workflow_data: dict[Any, Any] global workflow data.
        :type workflow_data: dict[Any, Any] | None
        :param user_agent_params: dict[str, Any] params of user agent.
        :type user_agent_params: dict[str, Any] | None
        :param auth_middleware_manager: AuthMiddlewareManager instance of auth middleware manager.
        :type auth_middleware_manager: AuthMiddlewareManager | None
        :param registration_config: instance of RegistrationConfig for register account.
        :type registration_config: RegistrationConfig | None
        :param token_suffix: The token suffix value.
        :type token_suffix: str | None
        :raises RuntimeError: If transport or protocol or mapper cannot be None.
        """

        from ..models import (
            DeviceType,
            TransportRegistry,
            EncodingRegistry,
            ProtocolRegistry,
            MapperRegistry,
        )

        default_mapper_conf = type(ExtraConfig().mapper)

        if extra_config is None:
            device_type = device_type or DeviceType.Web

            if device_type is None:
                # dummy for type-checker, because it see it by "str | DeviceType | None | Literal[DeviceType.Web]",
                # not "str | DeviceType"
                raise RuntimeError("Never")

            extra_config = ExtraConfig(
                mapper=default_mapper_conf(
                    token=token,
                    password=password,
                    device_type=device_type,
                    phone=phone,
                )
            )
            extra_config = extra_config.config_rebuild(
                transport=transport,
                protocol=protocol,
                encoding=encoding,
                mapper=mapper,
            )

        else:
            device_type = (
                device_type or extra_config.mapper.device_type or DeviceType.Web
            )

            if device_type is None:
                # dummy for type-checker, because it see it by "str | DeviceType | None | Literal[DeviceType.Web]",
                # not "str | DeviceType"
                raise RuntimeError("Never")

            extra_config.mapper.device_type = device_type
            extra_config = extra_config.config_rebuild(
                transport=transport,
                encoding=encoding,
                protocol=protocol,
                mapper=mapper,
            )

        transport = cast(
            TransportRegistry, from_config_to_registry(type(extra_config.transport))
        )
        encoding = cast(
            EncodingRegistry, from_config_to_registry(type(extra_config.encoding))
        )
        protocol = cast(
            ProtocolRegistry, from_config_to_registry(type(extra_config.protocol))
        )
        mapper = cast(
            MapperRegistry, from_config_to_registry(type(extra_config.mapper))
        )

        if workflow_data is None:
            workflow_data = {}

        logger = logging.getLogger("MaxApi")

        if transport not in TRANSPORTS:
            raise RuntimeError(f"transport {transport} is not supported")

        if protocol not in PROTOCOLS:
            raise RuntimeError(f"protocol {protocol} is not supported")

        if mapper not in MAPPERS:
            raise RuntimeError(f"mapper {mapper} is not supported")

        logger.info("Start initialization...")

        max_encoding: BaseEncoding[Any, Any, Any, Any] = from_registry(
            ENCODINGS, encoding
        )(extra_config)

        logger.info("Initializing transport...")

        max_transport = await from_registry(TRANSPORTS, transport)(
            max_encoding, extra_config
        )
        logger.info("Transport initialized.")

        logger.info("Initializing protocol...")
        protocol_res: Any = await from_registry(PROTOCOLS, protocol)(
            transport=max_transport,
            encoding=max_encoding,
            extra_config=extra_config,
        )
        max_protocol: BaseMaxProtocol[Any, Any] = protocol_res
        logger.info("Protocol initialized.")

        logger.info("Initializing mapper...")
        map_class = from_registry(MAPPERS, mapper)
        max_mapper = await map_class(
            self,
            protocol=max_protocol,
            extra_config=extra_config,
        )
        logger.info("Mapper initialized.")

        hide_func_call(
            type(self).__init__,
            self,
            protocol=max_protocol,
            password=password,
            transport=max_transport,
            mapper=max_mapper,
            token=token,
            logger=logger,
            workflow_data=workflow_data,
            device_type=device_type,
            auth_middleware_manager=auth_middleware_manager,
            extra_config=extra_config,
        )

        if token is None and self.auth_middleware_manager is not None:
            from ..models.AuthFlow import AuthFlow

            await self.mapper.start_auth_flow(
                device_type=device_type,
                password=password,
                # user_agent_params=user_agent_params,
                # registration_config=registration_config,
                # token_suffix=token_suffix,
                **kwargs,
            )

            mapper_type = type(self.mapper)
            protocol_type = type(self.protocol)
            transport_type = type(self.transport)

            auth_alias = AuthFlow[
                mapper_type,  # type: ignore[valid-type]
                protocol_type,  # type: ignore[valid-type]
                transport_type,  # type: ignore[valid-type]
            ]

            async def auth_wrapped(
                auth_flow: AuthFlow[Any, Any, Any],
                _: dict[Any, Any],
            ) -> AuthFlow[Any, Any, Any]:
                """Auth wrapped.

                :param auth_flow: AuthFlow[Any, Any, Any] instance to process.
                :type auth_flow: AuthFlow[Any, Any, Any]
                :param _: dict[Any, Any] instance to process.
                :type _: dict[Any, Any]
                :returns: The resulting AuthFlow[Any, Any, Any] value.
                :rtype: AuthFlow[Any, Any, Any]
                """
                return auth_flow

            wrapped = self.auth_middleware_manager.wrap_middlewares(
                self.auth_middleware_manager,
                auth_wrapped,
            )

            auth_alias.model_rebuild(
                _types_namespace={
                    "MaxApi": type(self),
                }
            )

            flow = auth_alias(
                mapper=self.mapper,
                protocol=self.protocol,
                transport=self.transport,
            )
            flow.as_(self)

            data = {
                type(self): self,
                mapper_type: self.mapper,
                protocol_type: self.protocol,
                transport_type: self.transport,
            }

            resolved_flow = await wrapped(flow, cast(dict[Any, Any], data))
            token = resolved_flow.token
            if token:
                await self.mapper.end_auth_flow(token)
            else:
                await self.mapper.end_auth_flow(None)

        await self.mapper.start(
            # token=token,
            # device_type=device_type,
            # password=password,
            # user_agent_params=user_agent_params,
            # registration_config=registration_config,
            # token_suffix=token_suffix,
            # **kwargs,
        )

    def __init__(
        self,
        device_type: str = "WEB",
        password: str | None = None,
        transport: BaseTransport[Any] | None = None,
        encoding: BaseEncoding[Any, Any, Any, Any] | None = None,
        protocol: BaseMaxProtocol[Any, Any] | None = None,
        mapper: BaseMapper[Any, Any] | None = None,
        transport_options: dict[str, Any] | None = None,
        token: str | None = None,
        logger: logging.Logger | None = None,
        workflow_data: dict[Any, Any] | None = None,
        auth_middleware_manager: AuthMiddlewareManager | None = None,
        registration_config: RegistrationConfig | None = None,
        token_suffix: str | None = None,
        extra_config: ExtraConfig | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the max api.

        :param device_type: Device type reported to the API.
        :type device_type: str
        :param password: Optional account password.
        :type password: str | None
        :param token: Optional auth token.
        :type token: str | None
        :param transport: Transport backend name.
        :type transport: str
        :param protocol: Protocol backend name.
        :type protocol: str
        :param mapper: Mapper backend name.
        :type mapper: str
        :param transport_options: Keyword arguments passed to the transport constructor.
        :type transport_options: dict[str, Any] | None
        :param kwargs: Extra keyword arguments passed to mapper initialization.
        :type kwargs: Any

        :param workflow_data: dict[Any, Any] global workflow data.
        :type workflow_data: dict[Any, Any] | None
        :param user_agent_params: dict[str, Any] params of user agent.
        :type user_agent_params: dict[str, Any] | None
        :param auth_middleware_manager: AuthMiddlewareManager instance of auth middleware manager.
        :type auth_middleware_manager: AuthMiddlewareManager | None
        :param registration_config: instance of RegistrationConfig for register account.
        :type registration_config: RegistrationConfig | None
        :param token_suffix: The token suffix value.
        :type token_suffix: str | None
        :raises RuntimeError: If transport or protocol or mapper cannot be None.
        """
        if workflow_data is None:
            workflow_data = {}

        if logger is None:
            logger = logging.getLogger("MaxApi")

        if transport is None or protocol is None or mapper is None:
            raise RuntimeError("transport or protocol or mapper cannot be None")

        self.extra_config = extra_config

        self.transport = transport
        self.transport_options = transport_options
        self.protocol = protocol
        self.mapper = mapper
        self.token = token
        self.password = password
        self.id: int | None = None
        self.phone: str | None = None

        self.me: Profile | None = None
        self.chats: list[Chat] | None = None
        self.names: list[Name] | None = None
        self.contacts: list[Contact | None] = []
        self.users: dict[int, Contact] = {}

        self._logger: logging.Logger | None = logger
        self.workflow_data = workflow_data
        self.auth_middleware_manager = auth_middleware_manager

    async def __call__(
        self, class_of_method: type[BaseMaxApiMethod[Any]], *args: Any, **kwargs: Any
    ) -> Any:
        """Invoke the max api.

        :param class_of_method: MAX API method class to instantiate and execute.
        :type class_of_method: type[BaseMaxApiMethod[Any]]
        :param args: Positional arguments forwarded to the wrapped callable.
        :type args: Any
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :returns: The value returned by the wrapped callable or backend.
        :rtype: Any
        :raises RuntimeError: If try a call method before initialization, because logger has not been initialized.
        """
        if self._logger is None:
            raise RuntimeError(
                "Try a call method before initialization, because logger has not been initialized"
            )
        self._logger.debug("Calling MaxApi method: %s", class_of_method.__name__)
        method = class_of_method().as_(self)
        try:
            return await method(*args, **kwargs)
        except MapperTransportError as e:
            self._logger.error(
                "Mapper transport error while call method=%s: %s",
                class_of_method.__name__,
                e,
            )
            raise BaseMaxApiMethodError(
                "error while call method=%s: %s",
                class_of_method.__name__,
                e,
            ) from e

        except MapperApiError as e:
            self._logger.error(
                "Mapper API error while call method=%s: %s",
                class_of_method.__name__,
                e,
            )
            raise BaseMaxApiMethodError(
                "API error title=%s error=%s message=%s localized_message=%s",
                e.title,
                e.error,
                e.message,
                e.localized_message,
            ) from e

        except BaseMapperError as e:
            self._logger.error(
                "Mapper unknown error while call method=%s: %s",
                class_of_method.__name__,
                e,
            )
            raise BaseMaxApiMethodError(
                "error while call method=%s: %s",
                class_of_method.__name__,
                e,
            ) from e

    def listen_updates(
        self, context: Any
    ) -> tuple[Callable[[Response], MaxObject], AsyncGenerator[Response, None]]:
        """Yield incoming updates forever.

        :param context: Runtime context passed to the mapper.
        :type context: Any

        :returns: Stream of incoming updates.
        :rtype: tuple[Callable[[Response], MaxObject], AsyncGenerator[Response, None]]
        """
        return self.mapper.listen_updates(context=context)
