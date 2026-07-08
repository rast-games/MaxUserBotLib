from __future__ import annotations

import types
from typing import TYPE_CHECKING, Any

from .StandardMaxEventObserver import StandardMaxEventObserver
from ...models import BaseMaxObject
from .UpdateType import Update, MaxObject
from ...protocol import Response

if TYPE_CHECKING:
    from ..Router import Router


class UpdateMaxEventObserver(StandardMaxEventObserver[Response]):

    def __init__(self, router: Router, event_name: str, type_of_update: type[MaxObject] | types.UnionType) -> None:
        super().__init__(router, event_name, Response)
        self.really_type_of_update: type[MaxObject] | types.UnionType = type_of_update


    async def is_my_update(
            self,
            update: Update
    ) -> bool:
        return isinstance(update, self.really_type_of_update)