import json
import os
import time

import requests
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from ecdsa import SigningKey, NIST256p
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

BUF_SIZE = 65536


class ParcelWatcher(FileSystemEventHandler):
    def __init__(self, blockchain_endpoint, storage_endpoint):
        self.private_key = SigningKey.generate(curve=NIST256p)
        self.public_key = self.private_key.get_verifying_key()
        self.encoded_public_key = self.public_key.to_string(encoding='uncompressed')
        self.owner = SHA256.new(self.encoded_public_key).digest()[:20].hex().upper()

        self.blockchain_endpoint = blockchain_endpoint
        self.storage_endpoint = storage_endpoint

    def _upload_parcel(self, src_path):
        parcel_name = os.path.basename(src_path)
        parcel_path = os.path.dirname(src_path)

        # TODO https://github.com/amolabs/docs/blob/master/protocol.md#key-custody
        key = get_random_bytes(32)
        print("key: {}".format(key.hex()))
        cipher = AES.new(key, AES.MODE_CTR)

        with open(src_path, 'rb') as f:
            buf = f.read(BUF_SIZE)
            encrypted = []
            while len(buf) > 0:
                encrypted.append(cipher.encrypt(buf))
                buf = f.read(BUF_SIZE)

        custody = ""

        # TODO AUTH
        res = requests.post(
            "{}/api/v1/parcels".format(self.storage_endpoint),
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

        res = requests.get("{:s}/status".format(self.blockchain_endpoint)).json()
        last_height = res["result"]["sync_info"]["latest_block_height"]

        tx = {
            "type": "register",
            "payload": {
                "target": parcel_id,
                "custody": custody
            },
            "sender": self.owner,
            "fee": "0",
            "last_height": last_height,
        }

        self._sign_tx(tx)

        request_body = json.dumps(tx).replace('"', '\\"')

        res = requests.get('{:s}/broadcast_tx_sync?tx="{}"'.format(self.blockchain_endpoint, request_body))

        print(res.json())

        return res

    def _sign_tx(self, tx):
        raw_tx = json.dumps(tx).encode()
        msg = SHA256.new(raw_tx).digest()
        signature = self.private_key.sign(msg)
        assert self.public_key.verify(signature, msg)

        tx['signature'] = {
            'pubKey': self.encoded_public_key.hex(),
            'sig_bytes': signature.hex()
        }

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
