import boto3
import redis


class CephService:
    def __init__(self, access_key: str, secret_key: str, bucket_name: str,
                 location: str = 'ap-southeast-2', root_path: str = '/', dir_level: int = 3):
        boto3.setup_default_session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=location,
        )
        # Client for using low level apis
        self.client = boto3.client(service_name='s3', region_name=location)
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Paginator.ListObjects
        self.paginator = self.client.get_paginator('list_objects_v2')
        self.bucket_name = bucket_name
        self.root_path = root_path
        # TODO Read redis config
        self.redis = redis.StrictRedis()
        self.dir_level = dir_level
        self._init_directory()

    def list_objects_v2(self, Prefix='', Delimiter='', MaxKeys=1000):
        return self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=Prefix, Delimiter=Delimiter, MaxKeys=MaxKeys)

    def _init_directory(self):
        work_stack: [(str, int)] = [(self.root_path, 0)]

        while len(work_stack) > 0:
            prefix, level = work_stack.pop()

            if level == self.dir_level:
                if not self.redis.get(prefix.encode()):
                    self.redis.set(prefix.encode(), b'\x00')
                continue

            req = self.list_objects_v2(prefix, '/')

            for e in req.get('CommonPrefixes', []):
                work_stack.append((e['Prefix'], level + 1))

    def scan_not_uploaded_dir(self):
        not_uploaded = []
        for key in self.redis.scan_iter():
            if b'\x00' == self.redis.get(key):
                not_uploaded.append(key.decode())
        return not_uploaded

    def get_object_keys(self, prefix: str):
        starting_token = None
        pagination_config = {
            'PageSize': 100,
        }

        while True:
            if starting_token is not None:
                pagination_config['StartingToken'] = starting_token

            req = self.paginator.paginate(Bucket=self.bucket_name, Prefix=prefix, PaginationConfig=pagination_config)

            for c in req:
                print(c)

            if 'Marker' in req:
                starting_token = req['Marker']
            else:
                break
