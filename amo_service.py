import json
from collections import OrderedDict
from typing import Union

import requests
from Crypto.Cipher import AES
from ecdsa import SigningKey, NIST256p
from ecdsa.util import sha256
from loguru import logger

from crypto import public_key_encrypt


class AMOService:
    def __init__(self,
                 blockchain_endpoint: str,
                 storage_endpoint: str,
                 private_key: Union[SigningKey, str, None],
                 http_client=requests):
        if isinstance(private_key, str):
            self.private_key = SigningKey.from_string(bytes.fromhex(private_key), curve=NIST256p, hashfunc=sha256)
        elif private_key is None:
            self.private_key = SigningKey.generate(curve=NIST256p, hashfunc=sha256)

        self.public_key = self.private_key.get_verifying_key()
        self.encoded_public_key = self.public_key.to_string(encoding='uncompressed')
        self.owner = sha256(self.encoded_public_key).digest()[:20].hex().upper()

        self.blockchain_endpoint = blockchain_endpoint
        self.storage_endpoint = storage_endpoint
        self.http_client = http_client

    def _sign_tx(self, tx: dict) -> OrderedDict:
        ordered_tx = OrderedDict()
        keys = ['type', 'sender', 'fee', 'last_height', 'payload']
        for k in keys:
            ordered_tx[k] = tx[k]

        raw_tx = json.dumps(ordered_tx, separators=(',', ':')).encode()
        signature = self.private_key.sign(raw_tx, hashfunc=sha256)

        ordered_tx['signature'] = {
            'pubKey': self.encoded_public_key.hex(),
            'sig_bytes': signature.hex()
        }

        return ordered_tx

    def _make_tx(self, tx_type: str, payload: OrderedDict, fee: str = '0'):
        res = requests.get('{:s}/status'.format(self.blockchain_endpoint))
        res.raise_for_status()

        last_height = res.json()['result']['sync_info']['latest_block_height']

        return {
            'type': tx_type,
            'payload': payload,
            'sender': self.owner,
            'fee': fee,
            'last_height': last_height
        }

    def broadcast_tx(self, signed_tx: OrderedDict):
        dumped_body = json.dumps(signed_tx).replace('"', '\\"')
        res = self.http_client.get('{:s}/broadcast_tx_sync?tx="{}"'.format(self.blockchain_endpoint, dumped_body))
        res.raise_for_status()
        tx_result = res.json()['result']

        if tx_result['code'] != 0:
            logger.error('transaction fails\n{tx_result}', tx_result=tx_result)
            raise ValueError('transaction fails')
        return tx_result

    def register_parcel(self, parcel_id: str, custody: bytes) -> OrderedDict:
        tx = self._make_tx(
            'register',
            OrderedDict([('target', parcel_id), ('custody', custody.hex())])
        )

        signed_tx = self._sign_tx(tx)
        return signed_tx

    def grant_parcel(self, parcel_id: str, grantee: str, custody: bytes):
        tx = self._make_tx(
            'grant',
            OrderedDict([('parcel_id', parcel_id), ('grantee', grantee), ('custody', custody)])
        )

        signed_tx = self._sign_tx(tx)
        return signed_tx

    def _get_auth_header(self, operation: dict) -> dict:
        token = self._get_token(operation)
        return {
            'X-Auth-Token': token,
            'X-Public-Key': self.encoded_public_key.hex(),
            'X-Signature': self.private_key.sign(token.encode(), hashfunc=sha256).hex(),
            'Content-Type': 'application/json'
        }

    def _get_token(self, operation: dict) -> str:
        res = self.http_client.post('{}/api/v1/auth'.format(self.storage_endpoint), json={
            'user': self.owner,
            'operation': operation
        }, headers={
            'Content-Type': 'application/json'
        })
        res.raise_for_status()

        token = res.json()['token']
        return token

    @staticmethod
    def _get_encryption_key():
        return SigningKey.generate(curve=NIST256p, hashfunc=sha256).to_string()

    def upload_parcel(self, data: bytes) -> (str, bytes):
        enc_key = self._get_encryption_key()
        custody = public_key_encrypt(self.public_key, enc_key)

        cipher = AES.new(enc_key, AES.MODE_CTR, nonce=b'\x00')
        encrypted = cipher.encrypt(data)

        digested = sha256(encrypted).hexdigest()
        auth = self._get_auth_header({
            'name': 'upload',
            'hash': digested
        })

        res = self.http_client.post(
            '{}/api/v1/parcels'.format(self.storage_endpoint),
            json={
                'owner': self.owner,
                'metadata': {
                    'owner': self.owner,
                },
                'data': encrypted.hex()
            },
            headers=auth
        )

        res.raise_for_status()
        return res.json()['id'], custody
