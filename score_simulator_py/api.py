import json
import math
import random
from datetime import date as datelib
from pathlib import Path

import httpx
from decouple import config

from .models import Frame, FrameTeam, Result, ResultTeam
from .types import MatchesTypes, MatchTypes

MATCHES_URL = (
    "https://raw.githubusercontent.com/"
    "tanzhijian/score-simulator-data/release/matches.json"
)


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

    def fetch(self) -> MatchesTypes:
        proxy: str | None = config("SCORE_SIMULATOR_PROXY", default=None)
        response = httpx.get(MATCHES_URL, proxies=proxy)
        response.raise_for_status()
        data: MatchesTypes = response.json()
        return data

    def read(self) -> MatchesTypes:
        with open(self.file) as f:
            data: MatchesTypes = json.load(f)
        return data

    def save(self, data: MatchesTypes) -> None:
        self.mkdir()
        with open(self.file, "w") as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False))

    def get(self) -> MatchesTypes:
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

    def select(self, date: str, matches: MatchesTypes) -> list[MatchTypes]:
        return matches[date]


class Game:
    def __init__(self, match: MatchTypes) -> None:
        self.match = match

    def generate_xg(self, mu: float, sigma: float = 0.1) -> float:
        """使用逆变换法生成正态分布的随机数来得到 xg, 标准差先使用一点假设的数值"""
        u = random.random()
        z = math.sqrt(-2 * math.log(u)) * math.cos(
            2 * math.pi * random.random()
        )

        xg = mu + sigma * z
        if xg <= 0:
            xg = 0.01
        elif xg > 1:
            xg = 0.99

        return xg

    def attack(self) -> Frame:
        frame = Frame(home=FrameTeam(), away=FrameTeam())

        home_xg_per_shot = (
            self.match["home"]["xg"] / self.match["home"]["shots"]
        )
        away_xg_per_shot = (
            self.match["away"]["xg"] / self.match["away"]["shots"]
        )
        home_shot_percentage = self.match["home"]["shots"] / (
            self.match["home"]["shots"] + self.match["away"]["shots"]
        )
        shot_prob_per_minute = (
            (self.match["home"]["shots"] + self.match["away"]["shots"])
            / (
                (self.match["home"]["played"] + self.match["away"]["played"])
                / 2
            )
            / 90
        )

        if random.random() < shot_prob_per_minute:
            if random.random() < home_shot_percentage:
                frame.home.shot = True
                frame.home.xg = self.generate_xg(home_xg_per_shot)
                if random.random() < home_xg_per_shot:
                    frame.home.score = True
            else:
                frame.away.shot = True
                frame.away.xg = self.generate_xg(away_xg_per_shot)
                if random.random() < away_xg_per_shot:
                    frame.away.score = True
        return frame

    def play(self, fulltime: int = 90) -> Result:
        result = Result(
            home=ResultTeam(name=self.match["home"]["name"]),
            away=ResultTeam(name=self.match["away"]["name"]),
            competition=self.match["competition"]["name"],
        )

        for minute in range(fulltime):
            frame = self.attack()
            result.home.shots += frame.home.shot
            result.home.xg += frame.home.xg
            result.home.score += frame.home.score
            result.away.shots += frame.away.shot
            result.away.xg += frame.away.xg
            result.away.score += frame.away.score

            if frame.home.score:
                result.home.goal_minutes.append(minute)
            elif frame.away.score:
                result.away.goal_minutes.append(minute)

        result.timing = fulltime
        result.played = True

        return result

    def play_100(self, fulltime: int = 90, steps: int = 100) -> Result:
        results = [self.play(fulltime) for _ in range(steps)]
        result = sum(
            results,
            Result(
                home=ResultTeam(name=self.match["home"]["name"]),
                away=ResultTeam(name=self.match["away"]["name"]),
                competition=self.match["competition"]["name"],
                timing=fulltime,
                played=True,
            ),
        )
        return result / steps
