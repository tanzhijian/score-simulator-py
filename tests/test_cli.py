from typing import Any, Generator

import pytest
from typer.testing import CliRunner

from score_simulator_py.api import Matches
from score_simulator_py.cli import app
from score_simulator_py.types import MatchesTypes

runner = CliRunner()


@pytest.fixture(scope="module")
def env(
    matches: Matches, today_matches_data: MatchesTypes
) -> Generator[None, Any, None]:
    matches.save(today_matches_data)
    yield
    if matches.file.exists():
        matches.file.unlink()
    if matches.directory.exists():
        matches.directory.rmdir()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_play(env: Any) -> None:
    result = runner.invoke(app, ["play"])
    assert result.exit_code == 0


def test_play_100(env: Any) -> None:
    result = runner.invoke(app, ["play_100", "--steps=2"])
    assert result.exit_code == 0
