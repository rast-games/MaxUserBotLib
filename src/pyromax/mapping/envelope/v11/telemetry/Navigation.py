from __future__ import annotations

from enum import IntEnum
from random import Random

from pydantic import BaseModel


class Screen(IntEnum):
    BACKGROUND = 1
    CONTACTS = 100
    CHATS = 150
    SEARCH = 151
    CALLS = 300
    CHAT = 350
    SETTINGS = 450
    MINIAPP = 500


MAIN_TAB_PARAMS = {
    "source_type": 5,
    "source_id": 1,
    "tab_config": 2,
}


class ScreenTransition(BaseModel):
    model_config = {"frozen": True}

    screen: Screen
    weight: int


class RouteProfile(BaseModel):
    model_config = {"frozen": True}

    steps: int
    min_pause: float
    max_pause: float
    long_pause_chance: float
    min_long_pause: float
    max_long_pause: float
    back_chance: float

    def pause(self, rng: Random) -> float:
        if rng.random() < self.long_pause_chance:
            return rng.uniform(self.min_long_pause, self.max_long_pause)
        return rng.uniform(self.min_pause, self.max_pause)


class NavigationRules(BaseModel):
    model_config = {"frozen": True}

    profiles: dict[str, RouteProfile]
    graph: dict[Screen, tuple[ScreenTransition, ...]]

    def choose_profile(self, rng: Random) -> RouteProfile:
        name = rng.choice(tuple(self.profiles))
        return self.profiles[name]


DEFAULT_RULES = NavigationRules(
    profiles={
        "quick": RouteProfile(
            steps=2,
            min_pause=35.0,
            max_pause=95.0,
            long_pause_chance=0.05,
            min_long_pause=180.0,
            max_long_pause=420.0,
            back_chance=0.30,
        ),
        "browse": RouteProfile(
            steps=4,
            min_pause=70.0,
            max_pause=210.0,
            long_pause_chance=0.12,
            min_long_pause=240.0,
            max_long_pause=720.0,
            back_chance=0.22,
        ),
        "read": RouteProfile(
            steps=3,
            min_pause=140.0,
            max_pause=360.0,
            long_pause_chance=0.25,
            min_long_pause=420.0,
            max_long_pause=1200.0,
            back_chance=0.18,
        ),
    },
    graph={
        Screen.BACKGROUND: (
            ScreenTransition(screen=Screen.CHATS, weight=10),
            ScreenTransition(screen=Screen.SETTINGS, weight=1),
        ),
        Screen.CHATS: (
            ScreenTransition(screen=Screen.CHAT, weight=7),
            ScreenTransition(screen=Screen.CONTACTS, weight=2),
            ScreenTransition(screen=Screen.SEARCH, weight=2),
            ScreenTransition(screen=Screen.CALLS, weight=1),
            ScreenTransition(screen=Screen.SETTINGS, weight=1),
            ScreenTransition(screen=Screen.CHATS, weight=2),
        ),
        Screen.CHAT: (
            ScreenTransition(screen=Screen.CHATS, weight=8),
            ScreenTransition(screen=Screen.CHAT, weight=2),
            ScreenTransition(screen=Screen.SETTINGS, weight=1),
        ),
        Screen.CONTACTS: (
            ScreenTransition(screen=Screen.CHATS, weight=6),
            ScreenTransition(screen=Screen.CHAT, weight=2),
            ScreenTransition(screen=Screen.SEARCH, weight=1),
        ),
        Screen.SEARCH: (
            ScreenTransition(screen=Screen.CHATS, weight=5),
            ScreenTransition(screen=Screen.CHAT, weight=3),
            ScreenTransition(screen=Screen.CONTACTS, weight=1),
        ),
        Screen.CALLS: (
            ScreenTransition(screen=Screen.CHATS, weight=5),
            ScreenTransition(screen=Screen.CONTACTS, weight=2),
            ScreenTransition(screen=Screen.SETTINGS, weight=2),
        ),
        Screen.SETTINGS: (
            ScreenTransition(screen=Screen.CHATS, weight=7),
            ScreenTransition(screen=Screen.CONTACTS, weight=2),
            ScreenTransition(screen=Screen.CALLS, weight=2),
            ScreenTransition(screen=Screen.MINIAPP, weight=1),
        ),
        Screen.MINIAPP: (
            ScreenTransition(screen=Screen.SETTINGS, weight=3),
            ScreenTransition(screen=Screen.CHATS, weight=6),
        ),
    },
)


class NavigationPlanner:
    def __init__(
        self,
        rng: Random,
        rules: NavigationRules = DEFAULT_RULES,
    ) -> None:
        self.rng = rng
        self.rules = rules
        self.current_screen = Screen.BACKGROUND
        self.history: list[Screen] = []

    def new_profile(self) -> RouteProfile:
        return self.rules.choose_profile(self.rng)

    def next_screen(self, profile: RouteProfile) -> Screen:
        if self.history and self.rng.random() < profile.back_chance:
            self.current_screen = self.history.pop()
            return self.current_screen

        next_screen = self._weighted_choice(self.rules.graph[self.current_screen])
        if next_screen != self.current_screen:
            self.history.append(self.current_screen)
            if len(self.history) > 4:
                del self.history[0]
        self.current_screen = next_screen
        return next_screen

    def reset_to_background(self) -> None:
        self.current_screen = Screen.BACKGROUND
        self.history.clear()

    def _weighted_choice(
        self,
        transitions: tuple[ScreenTransition, ...],
    ) -> Screen:
        total = sum(item.weight for item in transitions)
        point = self.rng.randint(1, total)
        current = 0
        for item in transitions:
            current += item.weight
            if point <= current:
                return item.screen
        return transitions[-1].screen
