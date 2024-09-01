import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.event_type in ['modified', 'created', 'moved']:
            print(f'Change detected: {event.src_path}')
            subprocess.run(['streamlit', 'run', 'main.py'])

if __name__ == "__main__":
    path = '.'  # Directory to watch
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
