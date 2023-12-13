from typing import TypedDict


class CompetitionType(TypedDict):
    name: str
    logo: str


class TeamType(TypedDict):
    name: str
    logo: str
    shots: int
    xg: float
    score: int | None
    played: int


class MatchType(TypedDict):
    name: str
    utc_time: str
    finished: bool
    competition: CompetitionType
    home: TeamType
    away: TeamType


MatchesType = dict[str, list[MatchType]]
