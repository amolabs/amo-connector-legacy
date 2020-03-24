import io

import boto3


class S3Service:
    def __init__(self, credential: dict, s3: dict):
        self.s3 = boto3.resource('s3', **credential)
        self.client = boto3.client('s3', **credential)

    def get_content(self, bucket_name: str, key: str) -> bytes:
        obj = self.s3.Object(
            Bucket=bucket_name,
            Key=key
        )

        with io.BytesIO() as f:
            obj.download_fileobj(f)
            f.seek(0)
            content = f.read()
        return content

    def add_tag(self, bucket_name: str, key: str, value: str):
        # Do not use s3 resource Object.put
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.put
        self.client.put_object_tagging(
            Bucket=bucket_name,
            Key=key,
            Tagging={
                'TagSet': [
                    {
                        'Key': 'parcel_id',
                        'Value': value
                    }
                ]
            }
        )
