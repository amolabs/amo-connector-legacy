import unittest
from ecdsa import SigningKey, NIST256p
from crypto import public_key_decrypt, public_key_encrypt


class CryptoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.private_key = SigningKey.generate(curve=NIST256p)
        self.public_key = self.private_key.get_verifying_key()

    def test_custody(self):
        plain = b'this is test text'
        encrypted = public_key_encrypt(self.public_key, plain)
        decrypted = public_key_decrypt(self.private_key, encrypted)

        assert plain == decrypted
