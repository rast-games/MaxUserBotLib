from enum import IntFlag, auto


class PollFlags(IntFlag):
    FLAG_SETTINGS_ANONYMOUS = auto()
    FLAG_SETTINGS_MULTISELECT = auto()
    FLAG_SETTINGS_REVOTE = auto()
    FLAG_SETTINGS_CLOSED = auto()
    FLAG_SETTINGS_QUIZ = auto()
    FLAG_SETTINGS_CAN_FORWARD = auto()
