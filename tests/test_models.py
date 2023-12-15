import os
from pathlib import Path
from typing import Any, Generator

import pytest
import respx
from httpx import Response

from score_simulator_py.models import MATCHES_URL, Matches, Result, ResultTeam
from score_simulator_py.types import MatchesType

from .data import matches as matches_data


def test_result_team() -> None:
    team = ResultTeam(name="Arsenal")
    team.goal_minutes.append(9)
    assert team.goal_log == "9', "

    team.reset()
    assert len(team.goal_minutes) == 0


def test_result_reset() -> None:
    result = Result(
        home=ResultTeam(name="a", shots=1),
        away=ResultTeam(name="b", goal_minutes=[1]),
        competition="c",
    )
    result.reset()
    assert result.home.shots == 0
    assert len(result.away.goal_minutes) == 0


class TestResult:
    @pytest.fixture(scope="class")
    def result(self) -> Result:
        home = ResultTeam(
            "Arsenal", shots=20, xg=1.2, score=2, goal_minutes=[2, 89]
        )
        away = ResultTeam(
            "Man City", shots=12, xg=0.8, score=1, goal_minutes=[47]
        )
        r = Result(home=home, away=away, competition="Premier League")

        return r

    def test_build_progress_bar(self, result: Result) -> None:
        bar = result._build_progress_bar(50)
        assert len(bar) == 10
        assert bar.count("█") == 5

    def test_shots_progress_bar(self, result: Result) -> None:
        assert result.shots_progress_bar.count("█") == 6

    def test_xg_progress_bar(self, result: Result) -> None:
        assert result.xg_progress_bar.count("█") == 6

    def test_top_goal_periods(self, result: Result) -> None:
        goal_minutes = [20, 20, 89, 89, 47, 47, 8, 78]
        top_periods = result._top_goal_periods(goal_minutes, 3)
        assert top_periods == [20, 47, 89]

    def test_add(self, result: Result) -> None:
        result_2 = Result(
            home=ResultTeam(
                name="Arsenal", shots=6, score=1, xg=0.6, goal_minutes=[89]
            ),
            away=ResultTeam(name="Man City", shots=4, xg=0.4),
            competition="Premier League",
        )
        new_result = result + result_2
        assert new_result.home.shots == 26
        assert int(new_result.away.xg * 10) == 12
        assert new_result.home.goal_minutes == [2, 89, 89]

        new_result = sum(
            [result, result_2],
            Result(
                home=ResultTeam(name="Arsenal"),
                away=ResultTeam(name="Man City"),
                competition="Premier League",
            ),
        )
        assert new_result.home.shots == 26

    def test_divide(self, result: Result) -> None:
        divide_result = result._divide(2)
        assert divide_result.home.shots == 10
        assert int(divide_result.away.xg * 10) == 4
        assert divide_result.away.score == 0
        assert len(divide_result.home.goal_minutes) == 1
        assert len(divide_result.away.goal_minutes) == 0

        truediv_result = result / 2
        floordiv_result = result // 2
        assert truediv_result.home.shots == floordiv_result.home.shots


class TestMatches:
    @pytest.fixture(scope="class")
    def mock_route(self) -> Generator[respx.Route, Any, None]:
        with respx.mock:
            route = respx.get(MATCHES_URL).mock(
                return_value=Response(200, json=matches_data)
            )
            yield route

    @pytest.fixture
    def clean(self, matches: Matches) -> Generator[None, Any, None]:
        yield
        if matches.file.exists():
            matches.file.unlink()
        if matches.directory.exists():
            matches.directory.rmdir()

    def test_default_path(self) -> None:
        matches = Matches()
        assert matches.path is None

    def test_path_include_env(self) -> None:
        os.environ["SCORE_SIMULATOR_DATA"] = str(Path(Path.cwd(), "tests/tmp"))
        matches = Matches()
        assert matches.path == str(Path(Path.cwd(), "tests/tmp"))
        del os.environ["SCORE_SIMULATOR_DATA"]

    def test_path_setter(self, matches: Matches) -> None:
        assert matches.path == str(Path(Path.cwd(), "tests/tmp"))

    def test_default_dir(self) -> None:
        matches = Matches()
        directory = matches.directory
        assert str(directory) == str(Path(Path.home(), "score-simulator-data"))

    def test_dir_path_setter(self, matches: Matches) -> None:
        directory = matches.directory
        assert str(directory) == str(Path(Path.cwd(), "tests/tmp"))

    def test_mkdir(self, matches: Matches, clean: Any) -> None:
        matches.mkdir()
        assert matches.directory.exists()

    def test_file(self, matches: Matches) -> None:
        assert str(matches.file) == str(
            Path(Path.cwd(), "tests/tmp/matches.json")
        )

    def test_read_and_save(self, matches: Matches, clean: Any) -> None:
        matches.save(matches_data)
        data = matches.read()
        match = data["2023-12-08"][0]
        assert match["home"]["name"] == "Juventus"

    def test_fetch(
        self, matches: Matches, mock_route: respx.Route, clean: Any
    ) -> None:
        data = matches.fetch()
        assert mock_route.called
        match = data["2023-12-08"][0]
        assert match["home"]["name"] == "Juventus"

    def test_get_file_not_exists(
        self, matches: Matches, mock_route: respx.Route, clean: Any
    ) -> None:
        data = matches.get()
        assert mock_route.called
        match = data["2023-12-08"][0]
        assert match["home"]["name"] == "Juventus"

    def test_get_not_today(
        self, matches: Matches, mock_route: respx.Route, clean: Any
    ) -> None:
        not_today_matches_data = matches_data | {"2023-12-09": []}
        matches.save(not_today_matches_data)

        data = matches.get()
        assert mock_route.called
        match = data["2023-12-08"][0]
        assert match["home"]["name"] == "Juventus"

        with pytest.raises(KeyError):
            data["2023-12-09"]

    def test_get_today(
        self, matches: Matches, today_matches_data: MatchesType, clean: Any
    ) -> None:
        matches.save(today_matches_data)

        data = matches.get()
        match = data["2023-12-08"][0]
        assert match["home"]["name"] == "Juventus"

        today = list(today_matches_data.keys())[1]
        assert len(data[today]) == 0
