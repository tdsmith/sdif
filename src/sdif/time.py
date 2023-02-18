import re
from enum import Enum
from typing import Union
from typing_extensions import Self

import attr


class TimeCode(Enum):
    """TIME Code 020: Time explanation code"""

    no_time = "NT"
    no_swim = "NS"
    did_not_finish = "DNF"
    disqualified = "DQ"
    scratch = "SCR"


@attr.define(frozen=True)
class Time:
    centiseconds: int

    @classmethod
    def from_str(cls, s: str) -> Self:
        m = re.match(r"(\d+:)?(\d{1,2})\.(\d{2})", s)
        if not m:
            raise ValueError("Invalid time")
        time = int(m[3]) + 100 * int(m[2])
        if m[1]:
            time += (60 * 100) * int(m[1][:-1])
        return Time(time)

    def format(self) -> str:
        c = self.centiseconds % 100
        s = (self.centiseconds // 100) % 60
        m = self.centiseconds // (100 * 60)

        parts = [
            f"{m:d}:" if m else "",
            f"{s:02d}.{c:02d}",
        ]

        return "".join(parts)


TimeT = Union[TimeCode, Time]
