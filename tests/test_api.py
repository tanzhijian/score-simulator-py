import pytest
import respx
from httpx import Response

from score_simulator_py.api import MATCHES_URL, Game, get_data

from .data import matches as matches_data


@respx.mock
def test_get_data() -> None:
    respx.get(MATCHES_URL).mock(
        return_value=Response(status_code=200, json=matches_data)
    )
    matches = get_data()
    match = matches["2023-12-08"][0]
    assert match["home"]["name"] == "Juventus"


class TestGame:
    @pytest.fixture(scope="class")
    def game(self) -> Game:
        match = matches_data["2023-12-08"][0]
        return Game(match)

    def test_generate_xg(self, game: Game) -> None:
        xg = game.generate_xg(mu=0.1)
        assert 0 <= xg <= 1

    def test_build_progress_bar(self, game: Game) -> None:
        bar = game.build_progress_bar(50)
        assert len(bar) == 10

    def test_attack(self, game: Game) -> None:
        frame = game.attack()
        assert frame.home.shot >= 0

    def test_play(self, game: Game) -> None:
        result = game.play()
        assert result.home.score >= 0
        assert result.timing == 90
