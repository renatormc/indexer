from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time


class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f"Modified: {event.src_path}")

    def on_created(self, event):
        print(f"Created: {event.src_path}")

    def on_deleted(self, event):
        print(f"Deleted: {event.src_path}")


def watch_folder() -> None:
    folder = Path(".")
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(folder), recursive=True)
    observer.start()
    print(f"Watching for changes in: {folder.resolve()}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()