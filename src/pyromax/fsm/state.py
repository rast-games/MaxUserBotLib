from collections.abc import Iterator
import inspect
from typing import no_type_check, Any


from ..dispatcher.event import MaxObject
from ..models import DataDict


class RawState:
    """dummy for forwarding"""


class State:
    """
    State object
    """

    def __init__(self, state: str | None = None, group_name: str | None = None) -> None:
        """Initialize the state.

        :param state: FSM state.
        :type state: str | None
        :param group_name: The group name value.
        :type group_name: str | None
        """
        self._state = state
        self._group_name = group_name
        self._group: type[StatesGroup] | None = None

    @property
    def group(self) -> "type[StatesGroup]":
        """Group.

        :returns: The resulting 'type[StatesGroup]' value.
        :rtype: 'type[StatesGroup]'
        :raises RuntimeError: If the requested action cannot be completed.
        """
        if not self._group:
            msg = "This state is not in any group."
            raise RuntimeError(msg)
        return self._group

    @property
    def state(self) -> str | None:
        """State.

        :returns: The resulting str | None value.
        :rtype: str | None
        """
        if self._state is None or self._state == "*":
            return self._state

        if self._group_name is None and self._group:
            group = self._group.__full_group_name__
        elif self._group_name:
            group = self._group_name
        else:
            group = "@"

        return f"{group}:{self._state}"

    def set_parent(self, group: "type[StatesGroup]") -> None:
        """Set parent.

        :param group: 'type[StatesGroup]' instance to process.
        :type group: 'type[StatesGroup]'
        :raises ValueError: If the requested action cannot be completed.
        """
        if not issubclass(group, StatesGroup):
            msg = "Group must be subclass of StatesGroup"
            raise ValueError(msg)
        self._group = group

    def __set_name__(self, owner: "type[StatesGroup]", name: str) -> None:
        """Set name.

        :param owner: 'type[StatesGroup]' instance to process.
        :type owner: 'type[StatesGroup]'
        :param name: The name value.
        :type name: str
        """
        if self._state is None:
            self._state = name
        self.set_parent(owner)

    def __str__(self) -> str:
        """Str.

        :returns: The resulting str value.
        :rtype: str
        """
        return f"<State '{self.state or ''}'>"

    __repr__ = __str__

    def __call__(self, event: MaxObject, data: DataDict) -> bool:
        """Invoke the state.

        :param event: Incoming event to process.
        :type event: MaxObject
        :param data: Contextual data passed through the processing pipeline.
        :type data: DataDict
        :returns: True when the requested condition is satisfied; otherwise False.
        :rtype: bool
        """
        raw_state = data.get(RawState)
        if self.state == "*":
            return True
        return raw_state == self.state

    def __eq__(self, other: object) -> bool:
        """Eq.

        :param other: object instance to process.
        :type other: object
        :returns: True when the requested condition is satisfied; otherwise False.
        :rtype: bool
        """
        if isinstance(other, self.__class__):
            return self.state == other.state
        if isinstance(other, str):
            return self.state == other
        return NotImplemented

    def __hash__(self) -> int:
        """Hash.

        :returns: The resulting int value.
        :rtype: int
        """
        return hash(self.state)


class StatesGroupMeta(type):
    __parent__: type["StatesGroup"] | None
    __childs__: tuple[type["StatesGroup"], ...]
    __states__: tuple[State, ...]
    __state_names__: tuple[str, ...]
    __all_childs__: tuple[type["StatesGroup"], ...]
    __all_states__: tuple[State, ...]
    __all_states_names__: tuple[str, ...]

    @no_type_check
    def __new__(mcs, name, bases, namespace, **kwargs):
        """New.

        :param mcs: The mcs value.
        :param name: The name value.
        :param bases: The bases value.
        :param namespace: The namespace value.
        :param kwargs: Keyword arguments forwarded to the wrapped callable.
        """
        cls = super().__new__(mcs, name, bases, namespace)

        states = []
        childs = []

        for arg in namespace.values():
            if isinstance(arg, State):
                states.append(arg)
            elif inspect.isclass(arg) and issubclass(arg, StatesGroup):
                child = cls._prepare_child(arg)
                childs.append(child)

        cls.__parent__ = None
        cls.__childs__ = tuple(childs)
        cls.__states__ = tuple(states)
        cls.__state_names__ = tuple(state.state for state in states)

        cls.__all_childs__ = cls._get_all_childs()
        cls.__all_states__ = cls._get_all_states()

        # In order to ensure performance, we calculate this parameter
        # in advance already during the production of the class.
        # Depending on the relationship, it should be recalculated
        cls.__all_states_names__ = cls._get_all_states_names()

        return cls

    @property
    def __full_group_name__(cls) -> str:
        """Full group name.

        :returns: The resulting str value.
        :rtype: str
        """
        if cls.__parent__:
            return f"{cls.__parent__.__full_group_name__}.{cls.__name__}"
        return cls.__name__

    def _prepare_child(cls, child: type["StatesGroup"]) -> type["StatesGroup"]:
        """Prepare child.

        While adding `cls` for its children, we also need to recalculate
        the parameter `__all_states_names__` for each child
        `StatesGroup`. Since the child class appears before the
        parent, at the time of adding the parent, the child's
        `__all_states_names__` is already recorded without taking into
        account the name of current parent.

        :param child: type['StatesGroup'] instance to process.
        :type child: type['StatesGroup']
        :returns: The resulting type['StatesGroup'] value.
        :rtype: type['StatesGroup']
        """
        child.__parent__ = cls  # type: ignore[assignment]
        child.__all_states_names__ = child._get_all_states_names()
        return child

    def _get_all_childs(cls) -> tuple[type["StatesGroup"], ...]:
        """Retrieve all childs.

        :returns: The resulting tuple[type['StatesGroup'], ...] value.
        :rtype: tuple[type['StatesGroup'], ...]
        """
        result = cls.__childs__
        for child in cls.__childs__:
            result += child.__childs__
        return result

    def _get_all_states(cls) -> tuple[State, ...]:
        """Retrieve all states.

        :returns: The resulting tuple[State, ...] value.
        :rtype: tuple[State, ...]
        """
        result = cls.__states__
        for group in cls.__childs__:
            result += group.__all_states__
        return result

    def _get_all_states_names(cls) -> tuple[str, ...]:
        """Retrieve all states names.

        :returns: The resulting tuple[str, ...] value.
        :rtype: tuple[str, ...]
        """
        return tuple(state.state for state in cls.__all_states__ if state.state)

    def __contains__(cls, item: Any) -> bool:
        """Contains.

        :param item: The item value.
        :type item: Any
        :returns: True when the requested condition is satisfied; otherwise False.
        :rtype: bool
        """
        if isinstance(item, str):
            return item in cls.__all_states_names__
        if isinstance(item, State):
            return item in cls.__all_states__
        if isinstance(item, StatesGroupMeta):
            return item in cls.__all_childs__
        return False

    def __str__(self) -> str:
        """Str.

        :returns: The resulting str value.
        :rtype: str
        """
        return f"<StatesGroup '{self.__full_group_name__}'>"

    def __iter__(self) -> Iterator[State]:
        """Iter.

        :returns: Items produced by the iterator.
        :rtype: Iterator[State]
        """
        return iter(self.__all_states__)


class StatesGroup(metaclass=StatesGroupMeta):
    @classmethod
    def get_root(cls) -> type["StatesGroup"]:
        """Retrieve root.

        :returns: The resulting type['StatesGroup'] value.
        :rtype: type['StatesGroup']
        """
        if cls.__parent__ is None:
            return cls
        return cls.__parent__.get_root()

    def __call__(self, event: MaxObject, data: DataDict) -> bool:
        """Invoke the states group.

        :param event: Incoming event to process.
        :type event: MaxObject
        :param data: Contextual data passed through the processing pipeline.
        :type data: DataDict
        :returns: True when the requested condition is satisfied; otherwise False.
        :rtype: bool
        """
        raw_state = data.get(RawState)
        return raw_state in type(self).__all_states_names__

    def __str__(self) -> str:
        """Str.

        :returns: The resulting str value.
        :rtype: str
        """
        return f"StatesGroup {type(self).__full_group_name__}"


default_state = State()
any_state = State(state="*")
