from ecdsa import ECDH, NIST256p, SigningKey
from ecdsa.util import sha256
from Crypto.Hash import SHA256
from Crypto.Cipher import AES

DEFAULT_KEY = SHA256.new(b'keyencryptionkey').digest()


def public_key_encrypt(public_key, data):
    eph = SigningKey.from_string(DEFAULT_KEY, curve=NIST256p, hashfunc=sha256)
    ec = ECDH(curve=NIST256p, private_key=eph, public_key=public_key)
    key = ec.generate_sharedsecret_bytes()

    cipher = AES.new(key, AES.MODE_CTR, nonce=b'\x00')
    encrypted = cipher.encrypt(data)

    return encrypted


def public_key_decrypt(private_key, data):
    eph = SigningKey.from_string(DEFAULT_KEY, curve=NIST256p, hashfunc=sha256)
    ec = ECDH(curve=NIST256p, private_key=private_key, public_key=eph.get_verifying_key())
    key = ec.generate_sharedsecret_bytes()

    cipher = AES.new(key, AES.MODE_CTR, nonce=b'\x00')
    decrypted = cipher.decrypt(data)

    return decrypted
