import unittest
from grant_service import GrantService


class GrantServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.grant_service = GrantService({
            'blockchain_endpoint': 'http://139.162.116.176:26657',
            'storage_endpoint': '',
            'private_key': None
        })

    def testGrantService(self):
        def polling_mock(q):
            requests = [{
                'parcel_id': 'x',
                'grantee': 'y',
                'custody': 'z',
            }]

            for r in requests:
                q.put(r)

        self.grant_service.run(polling_mock)

