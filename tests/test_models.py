import pytest

from score_simulator_py.models import Game


class TestGame:
    @pytest.fixture(scope="class")
    def game(self) -> Game:
        return Game(
            home_shots=195,
            home_xg=22.7,
            home_played=15,
            away_shots=242,
            away_xg=25.6,
            away_played=15,
        )

    def test_generate_xg(self, game: Game) -> None:
        xg = game.generate_xg(mu=0.1)
        assert 0 <= xg <= 1

    def test_build_progress_bar(self, game: Game) -> None:
        bar = game.build_progress_bar(50)
        assert len(bar) == 10

    def test_attack(self, game: Game) -> None:
        frame = game.attack()
        assert frame.home_shot >= 0

    def test_play(self, game: Game) -> None:
        stats = game.play()
        assert stats.home_score >= 0
        assert stats.timing == 90
