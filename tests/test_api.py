import os
from pathlib import Path
from typing import Any, Generator

import pytest
import respx
from httpx import Response

from score_simulator_py.api import MATCHES_URL, Game, Matches
from score_simulator_py.types import MatchesTypes

from .data import matches as matches_data


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
        self, matches: Matches, today_matches_data: MatchesTypes, clean: Any
    ) -> None:
        matches.save(today_matches_data)

        data = matches.get()
        match = data["2023-12-08"][0]
        assert match["home"]["name"] == "Juventus"

        today = list(today_matches_data.keys())[1]
        assert len(data[today]) == 0

    def test_select(self, matches: Matches) -> None:
        selected = matches.select(date="2023-12-08", matches=matches_data)
        match = selected[0]
        assert match["home"]["name"] == "Juventus"


class TestGame:
    @pytest.fixture(scope="class")
    def game(self) -> Game:
        match = matches_data["2023-12-08"][0]
        return Game(match)

    def test_generate_xg(self, game: Game) -> None:
        xg = game.generate_xg(mu=0.1)
        assert 0 <= xg <= 1

    def test_attack(self, game: Game) -> None:
        frame = game.attack()
        assert frame.home.shot >= 0

    def test_play(self, game: Game) -> None:
        result = game.play()
        assert result.home.score >= 0
        assert result.timing == 90

    def test_play_100(self, game: Game) -> None:
        result = game.play_100(steps=2)
        assert result.home.score >= 0
        assert result.timing == 90
        assert result.played
