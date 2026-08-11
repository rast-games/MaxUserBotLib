from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Literal, overload

from ..state import State

StateType = str | State | None

DEFAULT_DESTINY = "default"


@dataclass(frozen=True)
class StorageKey:
    max_api_id: int
    chat_id: int
    user_id: int
    # thread_id: int | None = None
    # business_connection_id: str | None = None
    destiny: str = DEFAULT_DESTINY


class KeyBuilder(ABC):
    """Base class for key builder."""

    @abstractmethod
    def build(
        self,
        key: StorageKey,
        part: Literal["data", "state", "lock"] | None = None,
    ) -> str:
        """Build key to be used in storage's db queries

        :param key: contextual key
        :param part: part of the record
        :return: key to be used in storage's db queries

        :type key: StorageKey
        :type part: Literal['data', 'state', 'lock'] | None
        :returns: The resulting str value.
        :rtype: str
        """


class DefaultKeyBuilder(KeyBuilder):
    """
    Simple key builder with default prefix.

    Generates a colon-joined string with prefix, chat_id, user_id,
    optional bot_id, business_connection_id, destiny and field.

    Format:
     :code:`<prefix>:<bot_id?>:<business_connection_id?>:<chat_id>:<user_id>:<destiny?>:<field?>`
    """

    def __init__(
        self,
        *,
        prefix: str = "fsm",
        separator: str = ":",
        with_bot_id: bool = False,
        # with_business_connection_id: bool = False,
        with_destiny: bool = False,
    ) -> None:
        """Initialize the default FSM storage-key builder.

        :param prefix: prefix for all records
        :param separator: separator
        :param with_bot_id: include Bot id in the key
        :param with_business_connection_id: include business connection id
        :param with_destiny: include destiny key

        :type prefix: str
        :type separator: str
        :type with_bot_id: bool
        :type with_destiny: bool
        """
        self.prefix = prefix
        self.separator = separator
        self.with_bot_id = with_bot_id
        # self.with_business_connection_id = with_business_connection_id
        self.with_destiny = with_destiny

    def build(
        self,
        key: StorageKey,
        part: Literal["data", "state", "lock"] | None = None,
    ) -> str:
        """Build.

        :param key: Storage key.
        :type key: StorageKey
        :param part: Literal['data', 'state', 'lock'] instance to process.
        :type part: Literal['data', 'state', 'lock'] | None
        :returns: The resulting str value.
        :rtype: str
        :raises ValueError: If the requested action cannot be completed.
        """
        parts = [self.prefix]
        if self.with_bot_id:
            parts.append(str(key.max_api_id))
        # if self.with_business_connection_id and key.business_connection_id:
        #     parts.append(str(key.business_connection_id))
        parts.append(str(key.chat_id))
        # if key.thread_id:
        #     parts.append(str(key.thread_id))
        parts.append(str(key.user_id))
        if self.with_destiny:
            parts.append(key.destiny)
        elif key.destiny != DEFAULT_DESTINY:
            error_message = (
                "Default key builder is not configured to use key destiny other than the default."
                "\n\nProbably, you should set `with_destiny=True` in for DefaultKeyBuilder."
            )
            raise ValueError(error_message)
        if part:
            parts.append(part)
        return self.separator.join(parts)


class BaseStorage(ABC):
    """
    Base class for all FSM storages
    """

    @abstractmethod
    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        """Set state for specified key

        :param key: storage key
        :param state: new state

        :type key: StorageKey
        :type state: StateType
        """

    @abstractmethod
    async def get_state(self, key: StorageKey) -> str | None:
        """Get key state

        :param key: storage key
        :return: current state

        :type key: StorageKey
        :returns: The resulting str | None value.
        :rtype: str | None
        """

    @abstractmethod
    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:
        """Write data (replace)

        :param key: storage key
        :param data: new data

        :type key: StorageKey
        :type data: Mapping[str, Any]
        """

    @abstractmethod
    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        """Get current data for key

        :param key: storage key
        :return: current data

        :type key: StorageKey
        :returns: The resulting dict[str, Any] value.
        :rtype: dict[str, Any]
        """

    @overload
    async def get_value(self, storage_key: StorageKey, dict_key: str) -> Any | None:
        """Get single value from data by key

        :param storage_key: storage key
        :param dict_key: value key
        :return: value stored in key of dict or ``None``

        :type storage_key: StorageKey
        :type dict_key: str
        :returns: The resulting Any | None value.
        :rtype: Any | None
        """

    @overload
    async def get_value(
        self, storage_key: StorageKey, dict_key: str, default: Any
    ) -> Any:
        """Get single value from data by key

        :param storage_key: storage key
        :param dict_key: value key
        :param default: default value to return
        :return: value stored in key of dict or default

        :type storage_key: StorageKey
        :type dict_key: str
        :type default: Any
        :returns: The value returned by the wrapped callable or backend.
        :rtype: Any
        """

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
        data = await self.get_data(storage_key)
        return data.get(dict_key, default)

    async def update_data(
        self, key: StorageKey, data: Mapping[str, Any]
    ) -> dict[str, Any]:
        """Update date in the storage for key (like dict.update)

        :param key: storage key
        :param data: partial data
        :return: new data

        :type key: StorageKey
        :type data: Mapping[str, Any]
        :returns: The resulting dict[str, Any] value.
        :rtype: dict[str, Any]
        """
        current_data = await self.get_data(key=key)
        current_data.update(data)
        await self.set_data(key=key, data=current_data)
        return current_data.copy()

    @abstractmethod
    async def close(self) -> None:  # pragma: no cover
        """Close storage (database connection, file or etc.)
        """


class BaseEventIsolation(ABC):
    @abstractmethod
    @asynccontextmanager
    async def lock(self, key: StorageKey) -> AsyncGenerator[None, None]:
        """Isolate events with lock.
        Will be used as context manager

        :param key: storage key
        :return: An async generator

        :type key: StorageKey
        :yields: Items produced by the iterator.
        :ytype: AsyncGenerator[None, None]
        """
        yield None

    @abstractmethod
    async def close(self) -> None:
        """Close.
        """
        pass
