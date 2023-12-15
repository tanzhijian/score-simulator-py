import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import date as datelib
from pathlib import Path

import httpx
from decouple import config

from .types import MatchesType, MatchType

MATCHES_URL = (
    "https://raw.githubusercontent.com/"
    "tanzhijian/score-simulator-data/release/matches.json"
)


@dataclass
class ResultTeam:
    name: str
    shots: int = 0
    score: int = 0
    xg: float = 0
    goal_minutes: list[int] = field(default_factory=list)

    def reset(self) -> None:
        self.shots = 0
        self.score = 0
        self.xg = 0
        self.goal_minutes.clear()

    @property
    def goal_log(self) -> str:
        log = ""
        for minute in self.goal_minutes:
            log += f"{minute}', "
        return log


@dataclass
class Result:
    home: ResultTeam
    away: ResultTeam
    competition: str
    timing: int = 0
    played: bool = False

    def reset(self) -> None:
        self.home.reset()
        self.away.reset()
        self.timing = 0
        self.played = False

    def add(self, result: "Result") -> None:
        self.home.shots += result.home.shots
        self.home.score += result.home.shots
        self.home.xg += result.home.xg
        self.home.goal_minutes += result.home.goal_minutes

        self.away.shots += result.away.shots
        self.away.score += result.away.shots
        self.away.xg += result.away.xg
        self.away.goal_minutes += result.away.goal_minutes

    def _top_goal_periods(self, goal_minutes: list[int], n: int) -> list[int]:
        # 计算每个时段的进球次数
        goal_counts = Counter(goal_minutes)
        # 选择前 n 个进球次数最多的时段
        top_periods = [period for period, _ in goal_counts.most_common(n)]
        return sorted(top_periods)

    def average(self, divisor: int) -> None:
        self.home.shots //= divisor
        self.home.score //= divisor
        self.home.xg /= divisor
        self.home.goal_minutes = self._top_goal_periods(
            self.home.goal_minutes, self.home.score
        )

        self.away.shots //= divisor
        self.away.score //= divisor
        self.away.xg /= divisor
        self.away.goal_minutes = self._top_goal_periods(
            self.away.goal_minutes, self.away.score
        )

    def _build_progress_bar(self, progress: int | float) -> str:
        bar = ""
        for i in range(1, 11):
            bar += "█" if progress >= i * 10 else "░"
        return bar

    @property
    def shots_progress_bar(self) -> str:
        if (all_shots := self.home.shots + self.away.shots) > 0:
            shots_progress = self.home.shots / all_shots * 100
        else:
            shots_progress = 50
        return self._build_progress_bar(shots_progress)

    @property
    def xg_progress_bar(self) -> str:
        if (all_xg := self.home.xg + self.away.xg) > 0:
            xg_progress = self.home.xg / all_xg * 100
        else:
            xg_progress = 50
        return self._build_progress_bar(xg_progress)


@dataclass
class FrameTeam:
    shot: bool = False
    score: bool = False
    xg: float = 0


@dataclass
class Frame:
    home: FrameTeam
    away: FrameTeam


class Matches:
    def __init__(self) -> None:
        self._path: str | None = None

    @property
    def path(self) -> str | None:
        if self._path is not None:
            return self._path
        setting_path: str | None = config("SCORE_SIMULATOR_DATA", default=None)
        return setting_path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value

    @property
    def directory(self) -> Path:
        if self.path is not None:
            path = Path(self.path)
        else:
            path = Path(Path.home(), "score-simulator-data")

        return path

    def mkdir(self) -> None:
        if not self.directory.exists():
            self.directory.mkdir()

    @property
    def file(self) -> Path:
        return Path(self.directory, "matches.json")

    def fetch(self) -> MatchesType:
        proxy: str | None = config("SCORE_SIMULATOR_PROXY", default=None)
        response = httpx.get(MATCHES_URL, proxies=proxy)
        response.raise_for_status()
        data: MatchesType = response.json()
        return data

    def read(self) -> MatchesType:
        with open(self.file) as f:
            data: MatchesType = json.load(f)
        return data

    def save(self, data: MatchesType) -> None:
        self.mkdir()
        with open(self.file, "w") as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False))

    def get(self) -> MatchesType:
        self.mkdir()
        if self.file.exists():
            data = self.read()

            date = list(data.keys())[1]
            today = datelib.today().strftime("%Y-%m-%d")
            if date != today:
                data = self.fetch()
                self.save(data)
        else:
            data = self.fetch()
            self.save(data)
        return data

    def select(self, date: str) -> list[MatchType]:
        data = self.get()
        return data[date]
