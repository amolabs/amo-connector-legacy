import unittest
from watcher import ParcelWatcher
from watchdog.events import FileCreatedEvent


class WatcherTest(unittest.TestCase):

    def setUp(self) -> None:
        self.watcher = ParcelWatcher(
            "http://139.162.116.176:26657",
            "http://localhost:5000"
        )

    def tearDown(self) -> None:
        pass

    def testSmoke(self):
        event = FileCreatedEvent("./data/short_text.txt")
        self.watcher.on_created(event)

    def testRegister(self):
        self.watcher._register_parcel("AA", "AA")
