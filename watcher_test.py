import unittest
from watcher import ParcelWatcher
from watchdog.events import FileCreatedEvent


class WatcherTest(unittest.TestCase):

    def setUp(self) -> None:
        self.watcher = ParcelWatcher("http://localhost:5000")

        pass

    def tearDown(self) -> None:
        pass

    def testSmoke(self):
        event = FileCreatedEvent("./data/this_is_very_long_text.txt")
        self.watcher.on_created(event)
