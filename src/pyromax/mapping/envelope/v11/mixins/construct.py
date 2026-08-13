from __future__ import annotations
import asyncio
from asyncio import Task, Lock, Event
import logging
from typing import TYPE_CHECKING, Any, _ProtocolMeta, TypeVar
from collections.abc import Callable, Coroutine

from typing import cast, Protocol

from .....mixins import AsyncInitializerMixin, AsyncConstructorMeta
from .....protocol import EnvelopeProtocol
from ..payloads.models import BaseUserAgentMappingModel
from ..constants import DEVICE_TYPE_TO_USERAGENT_MODEL as DEVICE_TYPE_TO_USER_AGENT_MAP
from ..LifecycleManager import LifecycleManager
from ..telemetry import TelemetryManager
from .....utils import FingerprintGenerator, write_token, read_token

if TYPE_CHECKING:
    from .....core import MaxApi
    from ..Mapper import Mapper
    from .....models import RegistrationConfig, BaseMaxObject

T = TypeVar("T", bound="BaseMaxObject")


from .MixinProtocol import MixinProtocol

# ProtocolMeta: type = type(Protocol)


class AsyncInitializerMixinProtocol(AsyncConstructorMeta, _ProtocolMeta):
    pass


class ConstructorMixin(
    AsyncInitializerMixin, MixinProtocol, metaclass=AsyncInitializerMixinProtocol
):

    def __init__(
        self,
        protocol: EnvelopeProtocol,
        keepalive_ping_interval: int,
    ) -> None:
        """Initialize the constructor mixin.

        :param protocol: Protocol backend or protocol instance.
        :type protocol: EnvelopeProtocol
        :param keepalive_ping_interval: The keepalive ping interval value.
        :type keepalive_ping_interval: int
        """
        self.protocol = protocol
        self.protocol_version = 11
        self._keepalive_ping_interval = keepalive_ping_interval
        self._logger = logging.getLogger("MapperV11")
        self._keepalive_task: Task[Any] | None = None
        self.keep_alive_interactive: bool = True
        self._update_listener_task: Task[Any] | None = None
        self.token: str | None = None
        self.TOKEN_NAME = (
            "ENVELOPE_MAX_TOKEN_V11" + self.protocol.transport.__class__.__name__
        )
        self.max_api: MaxApi | None = None
        self._manage_lifecycle_task: Task[Any] | None = None
        self._update_listener_lock: Lock = Lock()
        self._authorized = asyncio.Event()
        self.request_timeout: int = 30
        self._telemetry: TelemetryManager | None = None
        self.user_agent: BaseUserAgentMappingModel | None = None
        self.fingerprint_generator = FingerprintGenerator()
        self.logged: bool = False
        self.password: str | None = None
        self.phone: str | None = None
        self.calls_seed: int | None = None
        self.sms_auth = False
        self._lifecycle_manager_inited: asyncio.Event = Event()
        self._mapper_connected: asyncio.Event = Event()
        self._protocol_connected: asyncio.Event = Event()

        self._lifecycle_manager: LifecycleManager | None = None

    @property
    def DEVICE_TYPE_TO_USERAGENT_MODEL(
        self,
    ) -> dict[str, type[BaseUserAgentMappingModel]]:
        """D e v i c e t y p e t o u s e r a g e n t m o d e l.

        :returns: The resulting dict[str, type[BaseUserAgentMappingModel]] value.
        :rtype: dict[str, type[BaseUserAgentMappingModel]]
        """
        return DEVICE_TYPE_TO_USER_AGENT_MAP

    async def _async_init(
        self,
        max_api: MaxApi,
        protocol: EnvelopeProtocol,
        *args: Any,
        keepalive_ping_interval: int = 30,
        **kwargs: Any,
    ) -> None:
        """Async init.

        :param max_api: MAX client to bind or use.
        :type max_api: MaxApi
        :param protocol: Protocol backend or protocol instance.
        :type protocol: EnvelopeProtocol
        :param args: Positional arguments forwarded to the wrapped callable.
        :type args: Any
        :param keepalive_ping_interval: The keepalive ping interval value.
        :type keepalive_ping_interval: int
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :raises TypeError: If max_api must be an instance of MaxApi.
        :raises TypeError: If protocol must be an instance of EnvelopeProtocol.
        """
        from .....core import MaxApi

        if not isinstance(max_api, MaxApi):
            raise TypeError("max_api must be an instance of MaxApi")
        if not isinstance(protocol, EnvelopeProtocol):
            raise TypeError("protocol must be an instance of EnvelopeProtocol")
        await asyncio.to_thread(self.__init__, protocol=protocol, keepalive_ping_interval=keepalive_ping_interval)  # type: ignore[misc]
        self.max_api = max_api

    async def initialize_client(
        self,
        token: str | None = None,
        device_id: str | None = None,
        protocol_version: int = 11,
        device_type: str = "WEB",
        password: str | None = None,
        phone: str | None = None,
        sms_auth: bool = False,
        interactive: bool = True,
        keep_alive_interactive: bool | None = None,
        url_callback: Callable[[str], Coroutine[Any, Any, Any]] | None = None,
        connection_timeout: int | None = None,
        user_agent_params: dict[str, Any] | None = None,
        registration_config: RegistrationConfig | None = None,
        use_mobile_fingerprint: bool = True,
        token_suffix: str | None = None,
        use_telemetry: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize client.

        :param token: Authentication token.
        :type token: str | None
        :param device_id: Identifier of the device.
        :type device_id: str | None
        :param protocol_version: The protocol version value.
        :type protocol_version: int
        :param device_type: The device type value.
        :type device_type: str
        :param password: Account password.
        :type password: str | None
        :param phone: Phone number in the format accepted by MAX.
        :type phone: str | None
        :param sms_auth: The sms auth value.
        :type sms_auth: bool
        :param interactive: The interactive value.
        :type interactive: bool
        :param keep_alive_interactive: The keep alive interactive value.
        :type keep_alive_interactive: bool | None
        :param url_callback: Callable to invoke.
        :type url_callback: Callable[[str], Coroutine[Any, Any, Any]] | None
        :param connection_timeout: The connection timeout value.
        :type connection_timeout: int | None
        :param user_agent_params: dict[str, Any] instance to process.
        :type user_agent_params: dict[str, Any] | None
        :param registration_config: RegistrationConfig instance to process.
        :type registration_config: RegistrationConfig | None
        :param use_mobile_fingerprint: Whether to use mobile fingerprint.
        :type use_mobile_fingerprint: bool
        :param token_suffix: The token suffix value.
        :type token_suffix: str | None
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :raises RuntimeError: If the requested action cannot be completed.
        :raises RuntimeError: If cannot create a new lifecycle manager.
        """
        self.TOKEN_NAME = (
            "ENVELOPE_MAX_TOKEN_V11"
            + self.protocol.transport.__class__.__name__
            + device_type
            + (token_suffix or "")
        )

        if user_agent_params is None:
            user_agent_params = {
                "device_type": device_type,
            }
            if device_id is not None:
                user_agent_params["device_id"] = device_id

        if device_type not in self.DEVICE_TYPE_TO_USERAGENT_MODEL:
            raise RuntimeError(f"Unknown device type: {device_type}")
        user_agent_model = self.DEVICE_TYPE_TO_USERAGENT_MODEL[device_type]
        user_agent = user_agent_model.get_random_user_agent(**user_agent_params)
        self.user_agent = user_agent
        if token is None:
            token = await read_token(name_of_token=self.TOKEN_NAME)

        if token is not None:
            await write_token(token, self.TOKEN_NAME)
        self.token = token
        self.password = password
        self.phone = phone
        self.sms_auth = sms_auth
        if keep_alive_interactive is None:
            keep_alive_interactive = interactive
        self.keep_alive_interactive = keep_alive_interactive
        self.protocol_version = protocol_version
        from ..Mapper import Mapper

        self._lifecycle_manager = LifecycleManager(
            mapper=cast(Mapper, self), connect_timeout=connection_timeout
        )

        if self._lifecycle_manager is None:
            raise RuntimeError("Cannot create a new lifecycle manager")

        if use_telemetry:
            if self.max_api is None:
                raise RuntimeError("Mapper not bounded to MaxApi instance")
            self._telemetry = TelemetryManager(
                max_api=self.max_api,
                mapper=cast(Mapper, self),
            )

        self.protocol.set_generation_getter(self._lifecycle_manager.get_generation)
        self.protocol.set_exceptions_callback(
            self._lifecycle_manager.notify_about_exception
        )
        self._lifecycle_manager_inited.set()

        self._lifecycle_manager.start(
            url_callback=url_callback,
            registration_config=registration_config,
            use_mobile_fingerprint=use_mobile_fingerprint,
        )

        await self._protocol_connected.wait()

        self._logger.info("Mapper initialized")

    def bind_api_instance(self, obj: T) -> T:
        """Bind api instance.

        :param obj: T instance to process.
        :type obj: T
        :returns: The resulting T value.
        :rtype: T
        :raises RuntimeError: If cannot bind api instance without max_api.
        """
        if self.max_api is None:
            raise RuntimeError("Cannot bind api instance without max_api")

        obj.as_(self.max_api)
        return obj
