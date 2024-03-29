from collections import Counter
from dataclasses import dataclass, field


@dataclass
class ResultTeam:
    name: str
    shots: int = 0
    score: int = 0
    xg: float = 0
    goal_minutes: list[int] = field(default_factory=list)

    @property
    def goal_log(self) -> str:
        return ", ".join([f"{minute}'" for minute in self.goal_minutes])

    def reset(self) -> None:
        self.shots = 0
        self.score = 0
        self.xg = 0
        self.goal_minutes.clear()


@dataclass
class Result:
    home: ResultTeam
    away: ResultTeam
    competition: str
    timing: int = 0
    played: bool = False

    def __add__(self, result: "Result") -> "Result":
        home = ResultTeam(
            name=self.home.name,
            shots=self.home.shots + result.home.shots,
            score=self.home.score + result.home.score,
            goal_minutes=self.home.goal_minutes + result.home.goal_minutes,
        )
        away = ResultTeam(
            name=self.away.name,
            shots=self.away.shots + result.away.shots,
            score=self.away.score + result.away.score,
            xg=self.away.xg + result.away.xg,
            goal_minutes=self.away.goal_minutes + result.away.goal_minutes,
        )
        return Result(
            home=home,
            away=away,
            competition=self.competition,
            timing=self.timing,
            played=self.played,
        )

    def __truediv__(self, divisor: int) -> "Result":
        return self._divide(divisor)

    def __floordiv__(self, divisor: int) -> "Result":
        return self._divide(divisor)

    def _divide(self, divisor: int) -> "Result":
        home_score = self.home.score // divisor
        home = ResultTeam(
            name=self.home.name,
            shots=self.home.shots // divisor,
            score=home_score,
            xg=self.home.xg / divisor,
            goal_minutes=self._top_goal_periods(
                self.home.goal_minutes, home_score
            ),
        )
        away_score = self.away.score // divisor
        away = ResultTeam(
            name=self.away.name,
            shots=self.away.shots // divisor,
            score=away_score,
            xg=self.away.xg / divisor,
            goal_minutes=self._top_goal_periods(
                self.away.goal_minutes, away_score
            ),
        )
        return Result(
            home=home,
            away=away,
            competition=self.competition,
            timing=self.timing,
            played=self.played,
        )

    def _top_goal_periods(self, goal_minutes: list[int], n: int) -> list[int]:
        # 计算每个时段的进球次数
        goal_counts = Counter(goal_minutes)
        # 选择前 n 个进球次数最多的时段
        top_periods = [period for period, _ in goal_counts.most_common(n)]
        return sorted(top_periods)

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

    def reset(self) -> None:
        self.home.reset()
        self.away.reset()
        self.timing = 0
        self.played = False


@dataclass
class StepTeam:
    shot: bool = False
    score: bool = False
    xg: float = 0


@dataclass
class Step:
    home: StepTeam
    away: StepTeam
