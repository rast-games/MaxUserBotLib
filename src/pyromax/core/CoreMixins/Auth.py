from collections.abc import Callable, Coroutine
from typing import cast, Any

from ...methods import (
    Set2FaMethod,
    Remove2FaMethod,
    ChangePasswordMethod,
    Check2FaMethod,
    ApproveQrLoginMethod,
)
from ...models import (
    TwoFactorAction,
)
from .CoreMixinsProtocol import CoreMixinsProtocol


class AuthMixin(CoreMixinsProtocol):
    async def set_2fa(
        self,
        password: str,
        email: str | None = None,
        hint: str | None = None,
        email_code_getter: Callable[[str], Coroutine[Any, Any, str]] | None = None,
        two_factor_actions: list[TwoFactorAction] | None = None,
    ) -> None:
        """Set 2fa.

        :param password: New 2FA password.
        :type password: str
        :param email: Email address for 2FA, if required.
        :type email: str | None
        :param hint: Password hint, if required.
        :type hint: str | None
        :param email_code_getter: Callable to get password, first argument is phone number.
        :type email_code_getter: Callable[[str], Coroutine[Any, Any, str]] | None
        :param two_factor_actions: Collection of two factor actions.
        :type two_factor_actions: list[TwoFactorAction] | None
        """
        return cast(
            None,
            await self(
                Set2FaMethod,
                password=password,
                email=email,
                hint=hint,
                email_code_getter=email_code_getter,
                two_factor_actions=two_factor_actions,
            ),
        )

    async def remove_2fa(
        self,
        password: str,
        two_factor_actions: list[TwoFactorAction] | None = None,
        remove_2fa: bool = True,
    ) -> None:
        """Remove 2fa.

        :param password: Account password.
        :type password: str
        :param two_factor_actions: Collection of two factor actions.
        :type two_factor_actions: list[TwoFactorAction] | None
        :param remove_2fa: The remove 2fa value.
        :type remove_2fa: bool
        """
        return cast(
            None,
            await self(
                Remove2FaMethod,
                password=password,
                two_factor_actions=two_factor_actions,
                remove_2fa=remove_2fa,
            ),
        )

    async def change_password(
        self,
        password_old: str,
        password_new: str,
        hint: str | None = None,
        two_factor_actions: list[TwoFactorAction] | None = None,
    ) -> None:
        """Change password.

        :param password_old: The password old value.
        :type password_old: str
        :param password_new: The password new value.
        :type password_new: str
        :param hint: Password hint.
        :type hint: str | None
        :param two_factor_actions: Collection of two factor actions.
        :type two_factor_actions: list[TwoFactorAction] | None
        """
        return cast(
            None,
            await self(
                ChangePasswordMethod,
                password_old=password_old,
                password_new=password_new,
                hint=hint,
                two_factor_actions=two_factor_actions,
            ),
        )

    async def check_2fa(self) -> bool:
        """Check 2fa.

        :returns: True when the account has 2FA; otherwise False.
        :rtype: bool
        """
        return cast(
            bool,
            await self(
                Check2FaMethod,
            ),
        )

    async def approve_qr_login(self, qr_link: str) -> None:
        """Approve qr login.

        :param qr_link: Link to the authorization QR code.
        :type qr_link: str
        """
        return cast(
            None,
            await self(
                ApproveQrLoginMethod,
                qr_link=qr_link,
            ),
        )
