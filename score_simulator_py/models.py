import math
import random
from dataclasses import dataclass


@dataclass
class GameState:
    home_shots: int = 0
    home_score: int = 0
    home_xg: float = 0
    home_goal_log = ""

    away_shots: int = 0
    away_score: int = 0
    away_xg: float = 0
    away_goal_log: str = ""

    timing: int = 0
    shots_progress_bar: str = ""
    xg_progress_bar: str = ""
    played: bool = False


@dataclass
class AttackState:
    home_shot: bool = False
    home_score: bool = False
    home_xg: float = 0

    away_shot: bool = False
    away_score: bool = False
    away_xg: float = 0


class Game:
    def __init__(
        self,
        home_shots: int,
        home_xg: float,
        home_played: int,
        away_shots: int,
        away_xg: float,
        away_played: int,
    ) -> None:
        self.home_xg_per_shot = home_xg / home_shots
        self.away_xg_per_shot = away_xg / away_shots
        self.home_shot_percentage = home_shots / (home_shots + away_shots)
        self.shot_prob_per_minute = (
            (home_shots + away_shots) / ((home_played + away_played) / 2) / 90
        )

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

    def attack(self) -> AttackState:
        state = AttackState()
        if random.random() < self.shot_prob_per_minute:
            if random.random() < self.home_shot_percentage:
                state.home_shot = True
                state.home_xg = self.generate_xg(self.home_xg_per_shot)
                if random.random() < self.home_xg_per_shot:
                    state.home_score = True
            else:
                state.away_shot = True
                state.away_xg = self.generate_xg(self.away_xg_per_shot)
                if random.random() < self.away_xg_per_shot:
                    state.away_score = True
        return state

    def play(self, fulltime: int = 90) -> GameState:
        state = GameState()
        state.played = True

        for minute in range(fulltime):
            frame = self.attack()
            state.home_shots += frame.home_shot
            state.home_xg += frame.home_xg
            state.away_shots += frame.away_shot
            state.away_xg += frame.away_xg
            if frame.home_score:
                state.home_score += frame.home_score
                state.home_goal_log += f"{minute}', "

            state.timing += 1

        if (all_shots := state.home_shots + state.away_shots) > 0:
            shots_progress = state.home_shots / all_shots * 100
            state.shots_progress_bar = self.build_progress_bar(shots_progress)

        if (all_xg := state.home_xg + state.away_xg) > 0:
            xg_progress = state.home_xg / all_xg * 100
            state.xg_progress_bar = self.build_progress_bar(xg_progress)

        return state
