from datetime import date as datelib
from typing import Optional

import typer

from .api import Game, get_data

app = typer.Typer()


@app.command()
def version() -> None:
    print("0.1.0")


@app.command()
def play(date: Optional[str] = None) -> None:
    if date is None:
        date = datelib.today().strftime("%Y-%m-%d")
    matches = get_data()
    for match in matches[date]:
        game = Game(match)
        result = game.play()

        print(
            (
                f"{result.competition} - "
                f"{result.home.name} {result.home.score} : "
                f"{result.away.score} {result.away.name}"
            )
        )
