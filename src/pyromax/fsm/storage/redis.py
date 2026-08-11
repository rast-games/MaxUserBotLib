import json
from collections.abc import AsyncGenerator, Callable, Mapping
from contextlib import asynccontextmanager
from typing import Any, cast


from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool
from redis.asyncio.lock import Lock
from redis.typing import ExpiryT


from ...exceptions import DataNotDictLikeError
from ..state import State
from .base import (
    BaseEventIsolation,
    BaseStorage,
    DefaultKeyBuilder,
    KeyBuilder,
    StateType,
    StorageKey,
)

DEFAULT_REDIS_LOCK_KWARGS = {"timeout": 60}
_JsonLoads = Callable[..., Any]
_JsonDumps = Callable[..., str]


class RedisStorage(BaseStorage):
    """
    Redis storage requires the :code:`redis` package (:code:`pip install redis`)
    """

    def __init__(
        self,
        redis: Redis,
        key_builder: KeyBuilder | None = None,
        state_ttl: ExpiryT | None = None,
        data_ttl: ExpiryT | None = None,
        json_loads: _JsonLoads = json.loads,
        json_dumps: _JsonDumps = json.dumps,
    ) -> None:
        """Initialize Redis-backed FSM storage.

        :param redis: instance of Redis connection
        :param key_builder: builder that helps to convert contextual key to string
        :param state_ttl: TTL for state records
        :param data_ttl: TTL for data records

        :type redis: Redis
        :type key_builder: KeyBuilder | None
        :type state_ttl: ExpiryT | None
        :type data_ttl: ExpiryT | None
        :param json_loads: _JsonLoads instance to process.
        :type json_loads: _JsonLoads
        :param json_dumps: _JsonDumps instance to process.
        :type json_dumps: _JsonDumps
        """
        if key_builder is None:
            key_builder = DefaultKeyBuilder()
        self.redis = redis
        self.key_builder = key_builder
        self.state_ttl = state_ttl
        self.data_ttl = data_ttl
        self.json_loads = json_loads
        self.json_dumps = json_dumps

    @classmethod
    def from_url(
        cls,
        url: str,
        connection_kwargs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> "RedisStorage":
        """Create an instance of :class:`RedisStorage` with the specified connection url

        :param url: the connection url (i.e. :code:`redis://user:password@host:port/db`)
        :param connection_kwargs: see :code:`redis` docs
        :param kwargs: arguments passed to :class:`RedisStorage`
        :return: an instance of :class:`RedisStorage`

        :type url: str
        :type connection_kwargs: dict[str, Any] | None
        :type kwargs: Any
        :returns: The resulting 'RedisStorage' value.
        :rtype: 'RedisStorage'
        """
        if connection_kwargs is None:
            connection_kwargs = {}
        pool = ConnectionPool.from_url(url, **connection_kwargs)
        redis = Redis(connection_pool=pool)
        return cls(redis=redis, **kwargs)

    def create_isolation(self, **kwargs: Any) -> "RedisEventIsolation":
        """Create isolation.

        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :returns: The resulting 'RedisEventIsolation' value.
        :rtype: 'RedisEventIsolation'
        """
        return RedisEventIsolation(
            redis=self.redis, key_builder=self.key_builder, **kwargs
        )

    async def close(self) -> None:
        """Close.
        """
        await self.redis.aclose(close_connection_pool=True)

    async def set_state(
        self,
        key: StorageKey,
        state: StateType = None,
    ) -> None:
        """Set state.

        :param key: Storage key.
        :type key: StorageKey
        :param state: FSM state.
        :type state: StateType
        """
        redis_key = self.key_builder.build(key, "state")
        if state is None:
            await self.redis.delete(redis_key)
        else:
            await self.redis.set(
                redis_key,
                cast(str, state.state if isinstance(state, State) else state),
                ex=self.state_ttl,
            )

    async def get_state(
        self,
        key: StorageKey,
    ) -> str | None:
        """Retrieve state.

        :param key: Storage key.
        :type key: StorageKey
        :returns: The resulting str | None value.
        :rtype: str | None
        """
        redis_key = self.key_builder.build(key, "state")
        value = await self.redis.get(redis_key)
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return cast(str | None, value)

    async def set_data(
        self,
        key: StorageKey,
        data: Mapping[str, Any],
    ) -> None:
        """Set data.

        :param key: Storage key.
        :type key: StorageKey
        :param data: Contextual data passed through the processing pipeline.
        :type data: Mapping[str, Any]
        :raises DataNotDictLikeError: If the requested action cannot be completed.
        """
        if not isinstance(data, dict):
            msg = f"Data must be a dict or dict-like object, got {type(data).__name__}"
            raise DataNotDictLikeError(msg)

        redis_key = self.key_builder.build(key, "data")
        if not data:
            await self.redis.delete(redis_key)
            return
        await self.redis.set(
            redis_key,
            self.json_dumps(data),
            ex=self.data_ttl,
        )

    async def get_data(
        self,
        key: StorageKey,
    ) -> dict[str, Any]:
        """Retrieve data.

        :param key: Storage key.
        :type key: StorageKey
        :returns: The resulting dict[str, Any] value.
        :rtype: dict[str, Any]
        """
        redis_key = self.key_builder.build(key, "data")
        value = await self.redis.get(redis_key)
        if value is None:
            return {}
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return cast(dict[str, Any], self.json_loads(value))


class RedisEventIsolation(BaseEventIsolation):
    def __init__(
        self,
        redis: Redis,
        key_builder: KeyBuilder | None = None,
        lock_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the redis event isolation.

        :param redis: Redis instance to process.
        :type redis: Redis
        :param key_builder: KeyBuilder instance to process.
        :type key_builder: KeyBuilder | None
        :param lock_kwargs: dict[str, Any] instance to process.
        :type lock_kwargs: dict[str, Any] | None
        """
        if key_builder is None:
            key_builder = DefaultKeyBuilder()
        if lock_kwargs is None:
            lock_kwargs = DEFAULT_REDIS_LOCK_KWARGS
        self.redis = redis
        self.key_builder = key_builder
        self.lock_kwargs = lock_kwargs

    @classmethod
    def from_url(
        cls,
        url: str,
        connection_kwargs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> "RedisEventIsolation":
        """From url.

        :param url: Resource URL.
        :type url: str
        :param connection_kwargs: dict[str, Any] instance to process.
        :type connection_kwargs: dict[str, Any] | None
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :returns: The resulting 'RedisEventIsolation' value.
        :rtype: 'RedisEventIsolation'
        """
        if connection_kwargs is None:
            connection_kwargs = {}
        pool = ConnectionPool.from_url(url, **connection_kwargs)
        redis = Redis(connection_pool=pool)
        return cls(redis=redis, **kwargs)

    @asynccontextmanager
    async def lock(
        self,
        key: StorageKey,
    ) -> AsyncGenerator[None, None]:
        """Lock.

        :param key: Storage key.
        :type key: StorageKey
        :yields: Items produced by the iterator.
        :ytype: AsyncGenerator[None, None]
        """
        redis_key = self.key_builder.build(key, "lock")
        async with self.redis.lock(name=redis_key, **self.lock_kwargs, lock_class=Lock):
            yield None

    async def close(self) -> None:
        """Close.
        """
        pass
