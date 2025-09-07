from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

from database import DBSession
from indexer import index_pdf, on_delete_file


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, folder):
        super().__init__()
        self.just_created = {}  # path -> timestamp
        self.folder = Path(folder).resolve()

    
    def not_interesting(self, event):
        return event.is_directory or Path(event.src_path).suffix.lower() != ".pdf"

    def on_created(self, event):
        if self.not_interesting(event):
            return
        with DBSession() as db_session:
            index_pdf(db_session, Path(event.src_path), datetime.now().timestamp())
        self.just_created[event.src_path] = time.time()

    def on_modified(self, event):
        if self.not_interesting(event):
            return
        # Ignore modified events within 2 seconds of creation
        created_time = self.just_created.get(event.src_path)
        if created_time and time.time() - created_time < 2:
            return
        # Clean up old entries
        self.just_created.pop(event.src_path, None)
        with DBSession() as db_session:
            index_pdf(db_session, Path(event.src_path), datetime.now().timestamp())
       

    def on_deleted(self, event):
        if self.not_interesting(event):
            return
        with DBSession() as db_session:
            on_delete_file(db_session, Path(event.src_path))

    def on_moved(self, event):
        if self.not_interesting(event):
            return
        src_in_folder = str(Path(event.src_path).resolve()).startswith(str(self.folder))
        dest_in_folder = str(Path(event.dest_path).resolve()).startswith(str(self.folder))
        if src_in_folder and dest_in_folder:
            with DBSession() as db_session:
                index_pdf(db_session, Path(event.dest_path), datetime.now().timestamp())
        elif src_in_folder:
            with DBSession() as db_session:
                on_delete_file(db_session, Path(event.src_path))
        elif dest_in_folder:
            with DBSession() as db_session:
                index_pdf(db_session, Path(event.dest_path), datetime.now().timestamp())
            


def watch_folder() -> None:
    folder = Path(".")
    event_handler = ChangeHandler(folder)
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