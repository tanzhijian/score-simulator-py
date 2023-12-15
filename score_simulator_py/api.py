import math
import random

from .models import Frame, FrameTeam, Result, ResultTeam
from .types import MatchType


class Game:
    def __init__(self, match: MatchType) -> None:
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
