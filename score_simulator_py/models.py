from dataclasses import dataclass


@dataclass
class ResultTeam:
    name: str
    shots: int = 0
    score: int = 0
    xg: float = 0
    goal_log: str = ""


@dataclass
class Result:
    home: ResultTeam
    away: ResultTeam
    competition: str
    timing: int = 0
    shots_progress_bar: str = ""
    xg_progress_bar: str = ""
    played: bool = False


@dataclass
class FrameTeam:
    shot: bool = False
    score: bool = False
    xg: float = 0


@dataclass
class Frame:
    home: FrameTeam
    away: FrameTeam
