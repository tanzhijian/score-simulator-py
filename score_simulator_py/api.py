import httpx

from .types import Matches

MATCHES_URL = (
    "https://raw.githubusercontent.com/"
    "tanzhijian/score-simulator-data/release/matches.json"
)


def get_data() -> Matches:
    response = httpx.get(MATCHES_URL)
    json: Matches = response.json()
    return json
