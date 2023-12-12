import respx
from httpx import Response

from score_simulator_py.api import MATCHES_URL, get_data

from .test_types import matches_data


@respx.mock
def test_get_data() -> None:
    respx.get(MATCHES_URL).mock(
        return_value=Response(status_code=200, json=matches_data)
    )
    matches = get_data()
    match = matches["2023-12-08"][0]
    assert match["home"]["name"] == "Juventus"
