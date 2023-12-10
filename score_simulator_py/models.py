from dataclasses import dataclass
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


@dataclass
class GameState:
    home_shots: int = 0
    home_score: int = 0
    home_xg: float = 0
    home_goal_log: str = ""

    away_shots: int = 0
    away_score: int = 0
    away_xg: float = 0
    away_goal_log: str = ""

    timing: int = 0
    shots_progress: str = ""
    xg_progress: str = ""
    played: bool = False

    def reset(self) -> None:
        self.home_shots = 0
        self.home_score = 0
        self.home_xg = 0
        self.home_goal_log = ""

        self.away_shots = 0
        self.away_score = 0
        self.away_xg = 0
        self.away_goal_log = ""

        self.timing = 0
        self.shots_progress = ""
        self.xg_progress = ""
