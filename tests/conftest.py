from datetime import date as datelib
from pathlib import Path

import pytest

from score_simulator_py.api import Matches
from score_simulator_py.types import MatchesTypes

from .data import matches as matches_data


@pytest.fixture(scope="session")
def matches() -> Matches:
    tmp_path = str(Path(Path.cwd(), "tests/tmp"))
    mt = Matches()
    mt.path = tmp_path
    return mt


@pytest.fixture(scope="session")
def today_matches_data() -> MatchesTypes:
    today = datelib.today().strftime("%Y-%m-%d")
    return matches_data | {today: []}
