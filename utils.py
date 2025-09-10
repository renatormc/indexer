import os
from pathlib import Path
import shutil
import subprocess


def startfile(path: str | Path) -> None:
    if os.name == "nt":
        os.startfile(path) #type: ignore
    else:
        os.system(f'xdg-open "{path}"')

def get_linux_file_manager() -> str | None:
    for op in ['dolphin', 'nautilus', 'nemo']:
        if shutil.which(op) is not None:
            return op
    return None

def show_in_file_manager(path: str | Path) -> None:
    path = Path(path)
    if os.name == "nt":
        subprocess.Popen(["explorer.exe", "/select,", str(path)])
    else:
        file_manager = get_linux_file_manager()
        if not file_manager:
            raise Exception("file manager not found")
        if file_manager == "dolphin":
            subprocess.Popen([file_manager, "--select", str(path)])
        elif file_manager == "nautilus":
            subprocess.Popen([file_manager, "--select", str(path)])
        elif file_manager == "nemo":
            subprocess.Popen([file_manager, str(path)])