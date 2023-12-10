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


class GameState:
    def __init__(self) -> None:
        self._reset()
        self.played = False

    def _reset(self) -> None:
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

    def reset(self) -> None:
        self._reset()
