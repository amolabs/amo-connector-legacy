import os
import time

import requests
from Crypto.Hash import SHA256
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ParcelWatcher(FileSystemEventHandler):
    def __init__(self):
        self.owner = "0000000000000000000000000000000000000000"

    def _register_parcel(self, src_path):
        parcel_name = os.path.basename(src_path)
        parcel_path = os.path.dirname(src_path)

        # TODO AUTH
        res = requests.post(
            "http://localhost:5000/api/v1/parcels",
            json={
                "owner": self.owner,
                "metadata": {
                    "owner": self.owner,
                    "name": parcel_name,
                    "path": parcel_path
                },
                "data": "AA"
            }
        )

        res.raise_for_status()
        return res.json()["id"]

    def on_created(self, event):
        print(f'event type: {event.event_type}  path : {event.src_path}')
        sha256 = SHA256.new()
        if not os.path.exists(event.src_path):
            return
        if event.src_path.split('/')[-1].startswith('.'):
            return

        with open(event.src_path, 'rb') as f:
            block = f.read(4096)
            while len(block) > 0:
                sha256.update(block)
                block = f.read(4096)
        file_hash = sha256.digest().hex()

        parcel_id = ""
        try:
            parcel_id = self._register_parcel(event.src_path)
        except requests.HTTPError:
            print("fail to upload")
            return
        print("parcel_id", parcel_id)


if __name__ == '__main__':
    event_handler = ParcelWatcher()
    observer = Observer()
    observer.schedule(event_handler, path='/data/parcels/', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
