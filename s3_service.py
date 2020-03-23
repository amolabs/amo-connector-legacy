import io

import boto3


class S3Service:
    def __init__(self, credential: dict, s3: dict):
        self.s3 = boto3.resource('s3', **credential)
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Queue
        self.destination = self.s3.Bucket(s3['bucket'])
        self.tag = s3['tag']

        self.cache = dict()

    def _get_bucket(self, bucket_name: str):
        if bucket_name not in self.cache:
            self.cache[bucket_name] = self.s3.Bucket(bucket_name)

        bucket = self.cache[bucket_name]
        return bucket

    def get_content(self, bucket_name: str, key: str) -> bytes:
        bucket = self._get_bucket(bucket_name)
        obj = bucket.Object(key)

        f = io.BytesIO()
        obj.download_fileobj(f)
        f.seek(0)

        content = f.read()
        f.close()

        return content

    def add_tag(self, bucket_name: str, key: str, value: str):
        bucket = self._get_bucket(bucket_name)
        obj = bucket.Object(key)

        obj.put(
            Tagging='{}={}'.format(self.tag, value)
        )
