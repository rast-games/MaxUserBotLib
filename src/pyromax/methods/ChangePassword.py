from typing import Any, cast

from .Base import BaseMaxApiMethod
from ..models import TwoFactorAction

NoneType = type(None)


class ChangePasswordMethod(BaseMaxApiMethod[NoneType]):
    async def __call__(
        self,
        password_old: str,
        password_new: str,
        hint: str | None = None,
        two_factor_actions: list[TwoFactorAction] | None = None,
    ) -> None:
        if not self._max_api:
            raise RuntimeError("ChangePassword method not bound to MaxApi instance")
        return cast(
            None,
            await self._max_api.mapper.call_method(
                type(self),
                password_old=password_old,
                password_new=password_new,
                hint=hint,
                expected_capabilities=two_factor_actions,
            ),
        )
