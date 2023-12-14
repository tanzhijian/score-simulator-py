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

    def build_progress_bar(self, progress: int | float) -> str:
        bar = ""
        for i in range(1, 11):
            bar += "█" if progress >= i * 10 else "░"
        return bar

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
        result.played = True

        for minute in range(fulltime):
            frame = self.attack()
            result.home.shots += frame.home.shot
            result.home.xg += frame.home.xg
            result.home.score += frame.home.score
            result.away.shots += frame.away.shot
            result.away.xg += frame.away.xg
            result.away.score += frame.away.score

            if frame.home.score:
                result.home.goal_log += f"{minute}', "
            elif frame.away.score:
                result.away.goal_log += f"{minute}', "

            result.timing += 1

        if (all_shots := result.home.shots + result.away.shots) > 0:
            shots_progress = result.home.shots / all_shots * 100
            result.shots_progress_bar = self.build_progress_bar(shots_progress)

        if (all_xg := result.home.xg + result.away.xg) > 0:
            xg_progress = result.home.xg / all_xg * 100
            result.xg_progress_bar = self.build_progress_bar(xg_progress)

        return result
