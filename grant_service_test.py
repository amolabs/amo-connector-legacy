import unittest
from grant_service import GrantService
import json


class GrantServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.grant_service = GrantService({
            'blockchain_endpoint': 'http://139.162.116.176:26657',
            'storage_endpoint': '',
            'private_key': None
        }, 'explorer_endpoint')

    def testGrantService(self):
        def polling_mock(*args):
            q = args[0]

            with open('testdata/requests.json', 'r') as f:
                requests = json.load(f)

            for r in requests:
                q.put(r)

        self.grant_service.run(polling_mock)

