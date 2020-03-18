import json
import os
from collections import OrderedDict

import requests
from ecdsa import SigningKey, NIST256p
from ecdsa.util import sha256


# TODO Load private key
class AMOService:
    def __init__(self, blockchain_endpoint, storage_endpoint):
        self.private_key = SigningKey.generate(curve=NIST256p)
        self.public_key = self.private_key.get_verifying_key()
        self.encoded_public_key = self.public_key.to_string(encoding='uncompressed')
        self.owner = sha256(self.encoded_public_key).digest()[:20].hex().upper()

        self.blockchain_endpoint = blockchain_endpoint
        self.storage_endpoint = storage_endpoint

    def _sign_tx(self, tx: dict) -> OrderedDict:
        ordered_tx = OrderedDict()
        keys = ['type', 'sender', 'fee', 'last_height', 'payload']
        for k in keys:
            ordered_tx[k] = tx[k]

        raw_tx = json.dumps(ordered_tx, separators=(',', ':')).encode()
        signature = self.private_key.sign(raw_tx, hashfunc=sha256)
        assert self.public_key.verify(signature, raw_tx, hashfunc=sha256)

        ordered_tx['signature'] = {
            'pubKey': self.encoded_public_key.hex(),
            'sig_bytes': signature.hex()
        }

        return ordered_tx

    def broadcast_tx(self, signed_tx: OrderedDict):
        dumped_body = json.dumps(signed_tx).replace('"', '\\"')
        res = requests.get('{:s}/broadcast_tx_sync?tx="{}"'.format(self.blockchain_endpoint, dumped_body))
        return res

    def register_parcel(self, parcel_id: str, custody: bytes) -> OrderedDict:
        res = requests.get('{:s}/status'.format(self.blockchain_endpoint)).json()
        last_height = res['result']['sync_info']['latest_block_height']

        tx = {
            'type': 'register',
            'payload': OrderedDict([('target', parcel_id), ('custody', custody)]),
            'sender': self.owner,
            'fee': '0',
            'last_height': last_height,
        }

        signed_tx = self._sign_tx(tx)
        return signed_tx

    def _get_auth_header(self, operation: dict) -> dict:
        token = self._get_token(operation)
        return {
            'X-Auth-Token': token,
            'X-Public-Key': self.encoded_public_key,
            'X-Signature': self.private_key.sign(token, hashfunc=sha256),
            'Content-Type': 'application/json'
        }

    def _get_token(self, operation: dict) -> str:
        res = requests.post('{}/api/v1/auth'.format(self.storage_endpoint), json={
            'user': self.owner,
            'operation': operation
        }, headers={
            'Content-Type': 'application/json'
        })
        res.raise_for_status()

        token = res.json()['token']
        return token

    # Change for S3 backend
    def upload_parcel(self, src_path):
        parcel_name = os.path.basename(src_path)
        parcel_path = os.path.dirname(src_path)

        with open(src_path, 'rb') as f:
            data = f.read()

        digested = sha256(data).hexdigest()

        auth = self._get_auth_header({
            'name': 'upload',
            'hash': digested
        })

        res = requests.post(
            '{}/api/v1/parcels'.format(self.storage_endpoint),
            json={
                'owner': self.owner,
                'metadata': {
                    'owner': self.owner,
                    'name': parcel_name,
                    'path': parcel_path
                },
                'data': 'AA'
            }, headers=auth
        )

        res.raise_for_status()
        return res.json()['id']
