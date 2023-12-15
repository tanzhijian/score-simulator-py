from datetime import date as datelib
from typing import Optional

import typer

from .api import Game
from .models import Matches

app = typer.Typer()


@app.command()
def version() -> None:
    print("0.1.0")


@app.command()
def play(date: Optional[str] = None) -> None:
    if date is None:
        date = datelib.today().strftime("%Y-%m-%d")
    matches = Matches()
    for match in matches.select(date):
        game = Game(match)
        result = game.play()

        print(
            (
                f"{result.competition} - "
                f"{result.home.name} {result.home.score} : "
                f"{result.away.score} {result.away.name}"
            )
        )


@app.command(name="play_100")
def play_100(date: Optional[str] = None, steps: int = 100) -> None:
    if date is None:
        date = datelib.today().strftime("%Y-%m-%d")
    matches = Matches()
    for match in matches.select(date):
        game = Game(match)
        result = game.play_100(steps=steps)

        print(
            (
                f"{result.competition} - "
                f"{result.home.name} {result.home.score} : "
                f"{result.away.score} {result.away.name}"
            )
        )


if __name__ == "__main__":
    app()
