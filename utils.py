import os
from pathlib import Path


def startfile(path: str | Path) -> None:
    if os.name == "nt":
        os.startfile(path)
    else:
        os.system(f'xdg-open "{path}"')