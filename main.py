import logging
from pathlib import Path
import click
import config
from gui.gui import run_gui
from indexer import update_index
from models import init_db
from watch import watch_folder
import os

logging.basicConfig(
    filename=str(config.APPDIR / ".local/indexer.log"),
    level=logging.DEBUG,
    encoding="utf-8"
)


@click.group()
def cli():
    """Indexer."""
    pass


@cli.command()
@click.option("-w", required=False, help="Workpath")
def gui(w):
    if w:
        os.chdir(w)
    run_gui()


@cli.command()
def install():
    path = config.APPDIR / "dev.ps1" if os.name == "nt" else config.APPDIR / "dev"
    text = path.read_text(encoding="utf-8")
    text = text.replace("$PSScriptRoot", str(config.APPDIR))
    lines = text.splitlines()
    for i, line in enumerate(reversed(lines)):
        original_i = len(lines) - 1 - i
        if "#removeline" in line:
            lines.pop(original_i)
    text = "\n".join(lines)
    path = Path.home() / ".local/bin/r-index.ps1" if os.name == "nt" else Path.home() / ".local/bin/r-index"
    path.write_text(text, encoding="utf-8")
    print(f"Created script \"{path}\"")


@cli.command("update-index")
def update_index_():
    update_index()


@cli.command("init")
def init():
    init_db()


@cli.command()
def watch():
    watch_folder()


if __name__ == "__main__":
    cli()
