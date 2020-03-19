import unittest

from requests import HTTPError

from amo_service import AMOService


class AMOServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.amo_service = AMOService(
            "http://139.162.116.176:26657",
            "http://localhost:5000"
        )

    def test_something(self):
        try:
            parcel_id, custody = self.amo_service.upload_parcel(b"test")
        except HTTPError:
            self.fail('Http error occur')
        print(parcel_id, custody.hex())
