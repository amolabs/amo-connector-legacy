import os
import unittest

from ceph_service import CephService


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        access_key = os.environ.get('S3_ACCESS_KEY')
        secret_key = os.environ.get('S3_SECRET_KEY')
        bucket_name = os.environ.get('S3_BUCKET')
        root_directory = os.environ.get('S3_ROOT_DIR')

        if access_key is None or secret_key is None or bucket_name is None:
            raise KeyError

        self.cpeh_service = CephService(access_key, secret_key, bucket_name, root_path=root_directory)

    def test_something(self):
        dirs = self.cpeh_service.scan_not_uploaded_dir()
        for d in dirs:
            self.cpeh_service.get_object_keys(d)
