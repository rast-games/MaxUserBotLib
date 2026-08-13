from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from random import Random
from typing import TYPE_CHECKING

from pydantic import BaseModel

from .Navigation import (
    MAIN_TAB_PARAMS,
    NavigationPlanner,
    RouteProfile,
    Screen,
)
from .PayloadsConstructor import (
    TelemetryPayloadBuilder,
    now_ms,
)
from ..methods.immutable import SendTelemetryMethod
from ..payloads.models import TelemetryEventMappingModel

if TYPE_CHECKING:
    from .....core import MaxApi
    from ..Mapper import Mapper
    from .....models import Chat


class TelemetryTiming(BaseModel):
    model_config = {"frozen": True}

    startup_delay: tuple[float, float] = (15.0, 90.0)
    session_idle_delay: tuple[float, float] = (900.0, 2700.0)
    render_delay: tuple[float, float] = (0.15, 1.2)
    return_delay: tuple[float, float] = (12.0, 45.0)
    return_to_background_chance: float = 0.40
    open_chats_render_chance: float = 0.20


DEFAULT_TIMING = TelemetryTiming()


class TelemetryManager:
    def __init__(self, max_api: MaxApi, mapper: Mapper) -> None:
        self.max_api = max_api
        self.mapper = mapper
        self._rng = Random()
        self._timing = DEFAULT_TIMING
        self._planner = NavigationPlanner(self._rng)
        self._payloads = TelemetryPayloadBuilder(self._rng)
        self._task: asyncio.Task[None] | None = None
        self._action_id = 0
        if mapper.user_agent is None:
            raise RuntimeError("User agent not set")
        self._session_id = mapper.user_agent.client_session_id
        self._last_nav_time = now_ms()
        self._logger = logging.getLogger("TelemetryManager")

    async def start(self) -> None:
        if self._task and not self._task.done():
            self._logger.debug("telemetry start skipped: already running")
            return

        if not self._ready:
            self._logger.debug("max_api is not ready, wait...")
            await self.mapper._authorized.wait()
            self._logger.debug("max_api ready, start run")

        self._task = asyncio.create_task(
            self._run(),
            name="pyromax.telemetry",
        )
        self._logger.debug("telemetry started")

    async def stop(self) -> None:
        if not self._task:
            return

        task = self._task
        self._task = None
        if not task.done():
            task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        self._logger.debug("telemetry stopped")

    async def _run(self) -> None:
        try:
            await asyncio.sleep(self._between(self._timing.startup_delay))
            await self._send_events(
                [self._payloads.login(self._user_id, self._session_id)]
            )

            while True:
                self._session_id += 1
                events = await self._collect_session_events(self._planner.new_profile())
                await self._send_events(events)
                self._planner.reset_to_background()
                await asyncio.sleep(self._between(self._timing.session_idle_delay))

        except asyncio.CancelledError:
            raise
        except Exception:
            self._logger.debug("telemetry loop stopped by error", exc_info=True)
        finally:
            self._task = None

    async def _collect_session_events(
        self,
        profile: RouteProfile,
    ) -> list[TelemetryEventMappingModel]:
        events: list[TelemetryEventMappingModel] = []

        for _ in range(profile.steps):
            await asyncio.sleep(profile.pause(self._rng))
            if not self._ready:
                return events

            screen_from = self._planner.current_screen
            screen_to = self._planner.next_screen(profile)
            events.append(self._nav_event(screen_from, screen_to))

            render_events = await self._render_events(screen_to)
            events.extend(render_events)

        if (
            self._planner.current_screen != Screen.BACKGROUND
            and self._rng.random() < self._timing.return_to_background_chance
        ):
            await asyncio.sleep(self._between(self._timing.return_delay))
            screen_from = self._planner.current_screen
            self._planner.reset_to_background()
            events.append(self._nav_event(screen_from, Screen.BACKGROUND))

        return events

    async def _render_events(
        self, screen_to: Screen
    ) -> list[TelemetryEventMappingModel]:
        if screen_to == Screen.CHAT:
            await asyncio.sleep(self._between(self._timing.render_delay))
            return [self._payloads.open_chat(self._user_id, self._session_id)]

        if (
            screen_to == Screen.CHATS
            and self._rng.random() < self._timing.open_chats_render_chance
        ):
            await asyncio.sleep(self._between(self._timing.render_delay))
            return [self._payloads.open_chats(self._user_id, self._session_id)]

        return []

    async def _send_events(self, events: list[TelemetryEventMappingModel]) -> None:
        if not events or not self._ready:
            return

        try:
            await self.mapper.send(
                method=SendTelemetryMethod(
                    events=events,
                ),
                timeout=self.mapper.request_timeout,
            )
            self._logger.debug("telemetry sent events=%s", len(events))
        except asyncio.CancelledError:
            raise
        except Exception:
            self._logger.debug("telemetry send failed", exc_info=True)

    def _nav_event(
        self, screen_from: Screen, screen_to: Screen
    ) -> TelemetryEventMappingModel:
        event = self._payloads.navigation(
            user_id=self._user_id,
            session_id=self._session_id,
            screen_from=int(screen_from),
            screen_to=int(screen_to),
            prev_time=self._last_nav_time,
            action_id=self._next_action_id(),
            extra_params=self._source_params(screen_to),
        )
        self._last_nav_time = event.time
        return event

    def _source_params(self, screen_to: Screen) -> dict[str, int]:
        if screen_to == Screen.CHATS:
            return dict(MAIN_TAB_PARAMS)

        if screen_to != Screen.CHAT:
            return {}

        chat = self._pick_chat()
        if chat is None:
            return {
                "source_type": 1,
                "source_id": self._user_id,
            }

        return {
            "source_type": _chat_source_type(chat),
            "source_id": chat.id,
        }

    def _pick_chat(self) -> Chat | None:
        chats = self.max_api.chats or []
        if not chats:
            return None
        return self._rng.choice(chats)

    def _next_action_id(self) -> int:
        self._action_id = (self._action_id + 1) % 0xFFFFFFFF
        return self._action_id

    def _between(self, value: tuple[float, float]) -> float:
        return self._rng.uniform(*value)

    @property
    def _ready(self) -> bool:
        return (
            self.mapper._authorized.is_set()
            and self.max_api.me is not None
            and self.mapper.protocol.transport.connected
        )

    @property
    def _user_id(self) -> int:
        if self.max_api.me is None:
            raise RuntimeError("Telemetry requires authenticated profile")
        return self.max_api.me.contact.id


def _chat_source_type(chat: Chat) -> int:
    if str(chat.type) == "ChatType.DIALOG" or chat.type == "DIALOG":
        return 1
    return 2
