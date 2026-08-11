from collections.abc import Callable, Coroutine
from typing import Any, cast

from .Base import BaseMaxApiMethod
from ..models import TwoFactorAction

NoneType = type(None)


class Set2FaMethod(BaseMaxApiMethod[NoneType]):
    async def __call__(
        self,
        password: str,
        email: str | None = None,
        hint: str | None = None,
        email_code_getter: Callable[[str], Coroutine[Any, Any, str]] | None = None,
        two_factor_actions: list[TwoFactorAction] | None = None,
    ) -> None:
        """Execute the set2 fa MAX API method.

        :param password: Account password.
        :type password: str
        :param email: The email value.
        :type email: str | None
        :param hint: The hint value.
        :type hint: str | None
        :param email_code_getter: Callable to invoke.
        :type email_code_getter: Callable[[str], Coroutine[Any, Any, str]] | None
        :param two_factor_actions: Collection of two factor actions.
        :type two_factor_actions: list[TwoFactorAction] | None
        :raises RuntimeError: If set2Fa method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("Set2Fa method not bound to MaxApi instance")
        return cast(
            None,
            await self._max_api.mapper.call_method(
                type(self),
                password=password,
                email=email,
                hint=hint,
                email_code_getter=email_code_getter,
                two_factor_actions=two_factor_actions,
            ),
        )
