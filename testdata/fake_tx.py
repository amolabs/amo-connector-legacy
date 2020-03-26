#!python3
import json
import random
import sys

from ecdsa import SigningKey, NIST256p
from ecdsa.util import sha256

n = sys.argv[1]

txs = []
for i in range(int(n)):
    vk = SigningKey.generate(curve=NIST256p, hashfunc=sha256).get_verifying_key()
    pk = vk.to_string(encoding='uncompressed')
    addr = sha256(pk).digest()[:20].hex().upper()
    r = random.randint(1, 1000000000)

    tx = {
        "type": "request",
        "sender": addr,
        "fee": "0",
        "last_height": "0",
        "payload": {
            "target": ''.join([str(7).zfill(8), sha256(pk + bytes(r)).hexdigest()]).upper(),
            "payment": str(r)
        },
        "signature": {
            "sig_bytes": "",
            "pubKey": pk.hex().upper()
        }
    }

    txs.append(tx)

print(json.dumps(txs, indent=4))
