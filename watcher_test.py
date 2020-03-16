import unittest
from watcher import ParcelWatcher
from watchdog.events import FileCreatedEvent


class WatcherTest(unittest.TestCase):

    def setUp(self) -> None:
        self.watcher = ParcelWatcher("http://localhost:5000")

    def tearDown(self) -> None:
        pass

    def testSmoke(self):
        event = FileCreatedEvent("./data/short_text.txt")
        self.watcher.on_created(event)
