from collections.abc import Mapping
from typing import Any, overload


from .storage.base import BaseStorage, StateType, StorageKey


class FSMContext:
    def __init__(self, storage: BaseStorage, key: StorageKey) -> None:
        """Initialize the f s m context.

        :param storage: BaseStorage instance to process.
        :type storage: BaseStorage
        :param key: Storage key.
        :type key: StorageKey
        """
        self.storage = storage
        self.key = key

    async def set_state(self, state: StateType = None) -> None:
        """Set state.

        :param state: FSM state.
        :type state: StateType
        """
        await self.storage.set_state(key=self.key, state=state)

    async def get_state(self) -> str | None:
        """Retrieve state.

        :returns: The resulting str | None value.
        :rtype: str | None
        """
        return await self.storage.get_state(key=self.key)

    async def set_data(self, data: Mapping[str, Any]) -> None:
        """Set data.

        :param data: Contextual data passed through the processing pipeline.
        :type data: Mapping[str, Any]
        """
        await self.storage.set_data(key=self.key, data=data)

    async def get_data(self) -> dict[str, Any]:
        """Retrieve data.

        :returns: The resulting dict[str, Any] value.
        :rtype: dict[str, Any]
        """
        return await self.storage.get_data(key=self.key)

    @overload
    async def get_value(self, key: str) -> Any | None:
        """Retrieve value.

        :param key: Storage key.
        :type key: str
        :returns: The resulting Any | None value.
        :rtype: Any | None
        """
        ...

    @overload
    async def get_value(self, key: str, default: Any) -> Any:
        """Retrieve value.

        :param key: Storage key.
        :type key: str
        :param default: The default value.
        :type default: Any
        :returns: The value returned by the wrapped callable or backend.
        :rtype: Any
        """
        ...

    async def get_value(self, key: str, default: Any | None = None) -> Any | None:
        """Retrieve value.

        :param key: Storage key.
        :type key: str
        :param default: The default value.
        :type default: Any | None
        :returns: The resulting Any | None value.
        :rtype: Any | None
        """
        return await self.storage.get_value(
            storage_key=self.key, dict_key=key, default=default
        )

    async def update_data(
        self,
        data: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update data.

        :param data: Contextual data passed through the processing pipeline.
        :type data: Mapping[str, Any] | None
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        :type kwargs: Any
        :returns: The resulting dict[str, Any] value.
        :rtype: dict[str, Any]
        """
        if data:
            kwargs.update(data)
        return await self.storage.update_data(key=self.key, data=kwargs)

    async def clear(self) -> None:
        """Clear.
        """
        await self.set_state(state=None)
        await self.set_data({})
