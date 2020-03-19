import unittest
from watcher import ParcelWatcher
from watchdog.events import FileCreatedEvent
from ecdsa import SigningKey, NIST256p
from ecdsa.util import sha256


class WatcherTest(unittest.TestCase):

    def setUp(self) -> None:
        self.watcher = ParcelWatcher(
            "http://139.162.116.176:26657",
            "http://localhost:5000",
            SigningKey.from_string(sha256(b'testkey').digest(), curve=NIST256p, hashfunc=sha256)
        )

    def tearDown(self) -> None:
        pass

    def testSmoke(self):
        event = FileCreatedEvent("./data/short_text.txt")
        self.watcher.on_created(event)
