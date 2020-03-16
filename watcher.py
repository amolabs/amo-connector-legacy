import json
import os
import time

import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Random import get_random_bytes
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ParcelWatcher(FileSystemEventHandler):
    def __init__(self, endpoint):
        self.private_key = ECC.generate(curve="P-256")
        self.public_key = self.private_key.public_key()
        self.encoded_public_key = "04{:s}{:s}" \
            .format(hex(self.public_key.pointQ.x)[2:], hex(self.public_key.pointQ.y)[2:])
        self.owner = SHA256.new(bytes.fromhex(self.encoded_public_key)).digest()[:20].hex().upper()
        self.endpoint = endpoint

    def _upload_parcel(self, src_path):
        parcel_name = os.path.basename(src_path)
        parcel_path = os.path.dirname(src_path)

        # TODO https://github.com/amolabs/docs/blob/master/protocol.md#key-custody
        key = get_random_bytes(32)
        custody = ""

        # TODO AUTH
        res = requests.post(
            "{}/api/v1/parcels".format(self.endpoint),
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
        return res.json()["id"], custody

    def _register_parcel(self, parcel_id, custody):
        request_headers = {
            'Content-Type': 'application/json'
        }

        # TODO parse
        last_height = requests.get("{:s}/status".format(self.endpoint)).json()["last_height"]

        tx = json.dumps({
            "type": "register",
            "payload": {
                "target": parcel_id,
                "custody": custody
            },
            "sender": self.owner,
            "fee": "0",
            "last_height": last_height
        })

        request_body = json.dumps({
            "tx": "",
            "mode": "sync"
        })

        res = requests.post("{:s}/txs".format(self.endpoint), data=request_body, headers=request_headers)
        return res

    def on_created(self, event):
        print(f'event type: {event.event_type}  path : {event.src_path}')
        if not os.path.exists(event.src_path):
            return
        if event.src_path.split('/')[-1].startswith('.'):
            return

        try:
            (parcel_id, custody) = self._upload_parcel(event.src_path)
        except requests.HTTPError:
            print("fail to upload")
            return
        print("parcel_id", parcel_id)


if __name__ == '__main__':
    event_handler = ParcelWatcher("")
    observer = Observer()
    observer.schedule(event_handler, path='/data/parcels/', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
