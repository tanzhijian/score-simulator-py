from typing import TypedDict


class Competition(TypedDict):
    name: str
    logo: str


class Team(TypedDict):
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
    competition: Competition
    home: Team
    away: Team


Matches = dict[str, list[Match]]
