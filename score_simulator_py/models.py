from typing import TypedDict


class _Competition(TypedDict):
    name: str
    logo: str


class _Team(TypedDict):
    name: str
    logo: str
    shots: int
    xg: float
    score: int | None
    played: int


class Match(TypedDict):
    name: str
    utc_time: str
    finished: bool
    competition: _Competition
    home: _Team
    away: _Team
