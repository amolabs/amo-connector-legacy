import json
import unittest
from unittest.mock import Mock

from grant_service import GrantService


class GrantServiceTest(unittest.TestCase):
    class AMOBlockchainMock:
        def get(self, url: str, params=None):
            mock = Mock()
            if 'abci_query' in url:

                def mock_json():
                    return {
                        'result': {
                            'response': {
                                'code': 0,
                                'value': {
                                    'custody': '391b31c15035cfd18782149267d39361c61a7672f90f6fcedac27500fba25d00'
                                }
                            }
                        }
                    }

                mock.json = mock_json
            elif 'broadcast_tx_sync' in url:

                def mock_json():
                    return {
                        'result': {
                            'code': 0,
                        }
                    }

                mock.json = mock_json

            return mock

    def setUp(self) -> None:
        self.grant_service = GrantService({
            'blockchain_endpoint': 'http://139.162.116.176:26657',
            'storage_endpoint': '',
            'private_key': None
        }, 'explorer_endpoint', http_client=self.AMOBlockchainMock())

    def testGrantService(self):
        def polling_mock(*args):
            q = args[0]

            with open('testdata/requests.json', 'r') as f:
                requests = json.load(f)

            for r in requests:
                q.put(r)

        self.grant_service.run(polling_mock)
