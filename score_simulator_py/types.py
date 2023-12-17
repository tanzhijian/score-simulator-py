from typing import TypedDict


class CompetitionTypes(TypedDict):
    name: str
    logo: str


class TeamTypes(TypedDict):
    name: str
    logo: str
    shots: int
    xg: float
    score: int | None
    played: int


class MatchTypes(TypedDict):
    name: str
    utc_time: str
    finished: bool
    competition: CompetitionTypes
    home: TeamTypes
    away: TeamTypes


MatchesTypes = dict[str, list[MatchTypes]]
