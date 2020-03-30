import unittest

from requests import HTTPError

from amo_service import AMOService


class AMOServiceTest(unittest.TestCase):
    TARGET_STORAGE_ID = 123

    def setUp(self) -> None:
        self.amo_service = AMOService(
            "http://139.162.116.176:26657",
            "http://139.162.111.178:5000",
            None
        )

    def test_upload_parcel(self):
        try:
            parcel_id, custody = self.amo_service.upload_parcel(b"test")
            # STORAGE ID (4 bytes) + PARCEL ID (32 bytes)
            self.assertEqual(len(parcel_id), 8 + 64)
            self.assertEqual(bytes.fromhex(parcel_id[:8]), bytes(123).zfill(4))

        except HTTPError:
            self.fail('Http error occur')
        print(parcel_id, custody.hex())
