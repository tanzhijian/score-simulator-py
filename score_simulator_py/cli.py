from datetime import date as datelib
from typing import Optional

import typer

from .api import get_data, matches_play

app = typer.Typer()


@app.command()
def version() -> None:
    print("0.1.0")


@app.command()
def play(date: Optional[str] = None) -> None:
    if date is None:
        date = datelib.today().strftime("%Y-%m-%d")
    data = get_data()
    results = matches_play(date, data)
    for stats in results:
        print(f"{stats.home_score} : {stats.away_score}")
