import pytest

from score_simulator_py.api import Game

from .data import matches as matches_data


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
