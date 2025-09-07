from pathlib import Path
import os


APPDIR = Path(os.path.dirname(os.path.realpath(__file__)))

INDEXDIR = Path("indexdir")
THUMBSDIR = INDEXDIR / "thumbs"
SQLITE_FILE =  INDEXDIR / "index.sqlite3"
THUMB_PLACEHOLDER = APPDIR / "gui/assets/thumb_placeholder.png"