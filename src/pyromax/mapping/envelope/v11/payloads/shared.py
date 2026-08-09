from enum import IntFlag

from pydantic import ConfigDict, BaseModel


def to_camel_case(snake_str: str) -> str:
    words = snake_str.split("_")
    camel_case = [words[0].lower()] + [word.capitalize() for word in words[1:]]
    return "".join(camel_case)


CAMEL_CASE_CONFIG = ConfigDict(
    alias_generator=to_camel_case,
    validate_by_name=True,
)


class CamelCaseModel(BaseModel):
    model_config = CAMEL_CASE_CONFIG


class PollAnswerMappingModel(CamelCaseModel):
    text: str
    answer_id: int | None = None


class PollFlagsMappingModel(IntFlag):
    FLAG_SETTINGS_ANONYMOUS = 1
    FLAG_SETTINGS_MULTISELECT = 2
    FLAG_SETTINGS_REVOTE = 4
    FLAG_SETTINGS_CLOSED = 8
    FLAG_SETTINGS_QUIZ = 16
    FLAG_SETTINGS_CAN_FORWARD = 32
