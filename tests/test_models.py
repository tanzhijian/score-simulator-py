from score_simulator_py.models import GameState


def test_game_state() -> None:
    state = GameState()
    assert state.home_score == 0
    assert not state.played

    state.home_score += 1
    state.played = True
    assert state.home_score == 1
    assert state.played

    state.reset()
    assert state.home_score == 0
    assert state.played
