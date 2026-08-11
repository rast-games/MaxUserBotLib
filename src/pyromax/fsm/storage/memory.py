from asyncio import Lock
from collections import defaultdict
from collections.abc import AsyncGenerator, Hashable, Mapping
from contextlib import asynccontextmanager
from copy import copy
from dataclasses import dataclass, field
from typing import Any, overload

from .base import (
    BaseEventIsolation,
    BaseStorage,
    StateType,
    StorageKey,
)
from ..state import State
from ...exceptions import DataNotDictLikeError


@dataclass
class MemoryStorageRecord:
    data: dict[str, Any] = field(default_factory=dict)
    state: str | None = None


class MemoryStorage(BaseStorage):
    """
    Default FSM storage; uses a regular :class:`dict` to store data and
    does not persist it across restarts.

    .. warning::

        This storage is not recommended for production use, as all data is lost
        when the bot restarts
    """

    def __init__(self) -> None:
        """Initialize the memory storage.
        """
        self.storage: defaultdict[StorageKey, MemoryStorageRecord] = defaultdict(
            MemoryStorageRecord,
        )

    async def close(self) -> None:
        """Close.
        """
        pass

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        """Set state.

        :param key: Storage key.
        :type key: StorageKey
        :param state: FSM state.
        :type state: StateType
        """
        self.storage[key].state = state.state if isinstance(state, State) else state

    async def get_state(self, key: StorageKey) -> str | None:
        """Retrieve state.

        :param key: Storage key.
        :type key: StorageKey
        :returns: The resulting str | None value.
        :rtype: str | None
        """
        return self.storage[key].state

    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:
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
        self.storage[key].data = data.copy()

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        """Retrieve data.

        :param key: Storage key.
        :type key: StorageKey
        :returns: The resulting dict[str, Any] value.
        :rtype: dict[str, Any]
        """
        return self.storage[key].data.copy()

    @overload
    async def get_value(self, storage_key: StorageKey, dict_key: str) -> Any | None:
        """Retrieve value.

        :param storage_key: StorageKey instance to process.
        :type storage_key: StorageKey
        :param dict_key: The dict key value.
        :type dict_key: str
        :returns: The resulting Any | None value.
        :rtype: Any | None
        """
        ...

    @overload
    async def get_value(
        self, storage_key: StorageKey, dict_key: str, default: Any
    ) -> Any:
        """Retrieve value.

        :param storage_key: StorageKey instance to process.
        :type storage_key: StorageKey
        :param dict_key: The dict key value.
        :type dict_key: str
        :param default: The default value.
        :type default: Any
        :returns: The value returned by the wrapped callable or backend.
        :rtype: Any
        """
        ...

    async def get_value(
        self,
        storage_key: StorageKey,
        dict_key: str,
        default: Any | None = None,
    ) -> Any | None:
        """Retrieve value.

        :param storage_key: StorageKey instance to process.
        :type storage_key: StorageKey
        :param dict_key: The dict key value.
        :type dict_key: str
        :param default: The default value.
        :type default: Any | None
        :returns: The resulting Any | None value.
        :rtype: Any | None
        """
        data = self.storage[storage_key].data
        return copy(data.get(dict_key, default))


class DisabledEventIsolation(BaseEventIsolation):
    @asynccontextmanager
    async def lock(self, key: StorageKey) -> AsyncGenerator[None, None]:
        """Lock.

        :param key: Storage key.
        :type key: StorageKey
        :yields: Items produced by the iterator.
        :ytype: AsyncGenerator[None, None]
        """
        yield

    async def close(self) -> None:
        """Close.
        """
        pass


class SimpleEventIsolation(BaseEventIsolation):
    def __init__(self) -> None:
        # TODO: Unused locks cleaner is needed
        """Initialize the simple event isolation.
        """
        self._locks: defaultdict[Hashable, Lock] = defaultdict(Lock)

    @asynccontextmanager
    async def lock(self, key: StorageKey) -> AsyncGenerator[None, None]:
        """Lock.

        :param key: Storage key.
        :type key: StorageKey
        :yields: Items produced by the iterator.
        :ytype: AsyncGenerator[None, None]
        """
        lock = self._locks[key]
        async with lock:
            yield

    async def close(self) -> None:
        """Close.
        """
        self._locks.clear()
