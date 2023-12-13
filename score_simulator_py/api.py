import httpx

from .models import Game, GameState
from .types import Matches

MATCHES_URL = (
    "https://raw.githubusercontent.com/"
    "tanzhijian/score-simulator-data/release/matches.json"
)


def get_data() -> Matches:
    response = httpx.get(MATCHES_URL, proxies="http://127.0.0.1:7891")
    json: Matches = response.json()
    return json


def matches_play(date: str, data: Matches) -> list[GameState]:
    matches = data[date]
    results: list[GameState] = []
    for match in matches:
        game = Game(
            home_shots=match["home"]["shots"],
            home_xg=match["home"]["xg"],
            home_played=match["home"]["played"],
            away_shots=match["away"]["shots"],
            away_xg=match["away"]["xg"],
            away_played=match["away"]["played"],
        )
        stats = game.play()
        results.append(stats)
    return results
