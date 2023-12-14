import json
from dataclasses import dataclass
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
