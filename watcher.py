import os
import time

import requests
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from amo_service import AMOService

BUF_SIZE = 65536


class ParcelWatcher(FileSystemEventHandler):
    def __init__(self, blockchain_endpoint, storage_endpoint):
        self.amo_service = AMOService(blockchain_endpoint, storage_endpoint)

    def on_created(self, event):
        print(f'event type: {event.event_type}  path : {event.src_path}')
        if not os.path.exists(event.src_path):
            return
        if event.src_path.split('/')[-1].startswith('.'):
            return

        try:
            (parcel_id, custody) = self.amo_service.upload_parcel(event.src_path)
        except requests.HTTPError:
            print('fail to upload')
            return
        print('parcel_id', parcel_id)


if __name__ == '__main__':
    event_handler = ParcelWatcher('http://139.162.116.176:26657', 'http://localhost:5000')
    observer = Observer()
    observer.schedule(event_handler, path='/data/parcels/', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
