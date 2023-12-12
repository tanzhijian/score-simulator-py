import typer

app = typer.Typer()


@app.command()
def version() -> None:
    print("0.1.0")


@app.command()
def play() -> None:
    print("hello")
