from typing import cast

from .Base import BaseMaxApiMethod

NoneType = type(None)


class ApproveQrLoginMethod(BaseMaxApiMethod[NoneType]):
    async def __call__(
        self,
        qr_link: str,
    ) -> None:
        """Execute the approve qr login MAX API method.

        :param qr_link: The qr link value.
        :type qr_link: str
        :raises RuntimeError: If approveQrLogin method not bound to MaxApi instance.
        """
        if not self._max_api:
            raise RuntimeError("ApproveQrLogin method not bound to MaxApi instance")
        return cast(
            None,
            await self._max_api.mapper.call_method(
                type(self),
                qr_link=qr_link,
            ),
        )
