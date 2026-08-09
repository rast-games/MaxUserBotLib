from typing import Generic, cast

from mypy.types import RequiredType
from typing_extensions import TypeVar

from .base import BaseMaxObject
from .enum import PollFlags
from .Attachments import BaseFileAttachment



class PollVote(BaseMaxObject):
    timestamp: int
    user_id: int


class PollResult(BaseMaxObject):
    answer_id: int
    vote_count: int
    votes: list[PollVote]
    rate: int
    options: int


class PollState(BaseMaxObject):
    total: int = 0
    result: list[PollResult] | None = None
    voter_preview_ids: list[int]


NoneOrNever = TypeVar('NoneOrNever', default=None)


default = cast(int, None)
default_poll_state = cast(PollState, None)


class PollAnswer(BaseMaxObject, Generic[NoneOrNever]):
    text: str
    answer_id: int | NoneOrNever = default


class Poll(BaseFileAttachment, Generic[NoneOrNever]):
    title: str
    answers: list[PollAnswer[NoneOrNever]]
    settings: PollFlags

    poll_id: int | NoneOrNever = default
    version: int | NoneOrNever = default
    state: PollState | NoneOrNever = default_poll_state


# if TYPE_CHECKING:
#     class Poll(BaseMaxObject, Generic[NoneOrNever]):
#         title: str
#         answers: list[PollAnswer]
#         settings: PollFlags
#
#         poll_id: int | NoneOrNever
#         version: int | NoneOrNever
#         state: PollState | NoneOrNever
# else:

