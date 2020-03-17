import boto
import boto.s3.connection
import os

access_key = os.environ.get('S3_ACCESS_KEY')
secret_key = os.environ.get('S3_SECRET_KEY')
bucket_name = os.environ.get('S3_BUCKET')

print("using {} {}".format(access_key, secret_key))

if not access_key or not secret_key:
    exit(1)
    print("key is missing")

conn = boto.connect_s3(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    host='s3.ap-northeast-2.amazonaws.com',
    calling_format=boto.s3.connection.OrdinaryCallingFormat(),
)

print("---- buckets ----")
for bucket in conn.get_all_buckets():
    print("{}\t{}".format(bucket.name, bucket.creation_date))

bucket = conn.get_bucket(bucket_name)

print("---- files ----")
for key in bucket.list():
    print("{}\t{}\t{}".format(key.name, key.size, key.last_modified))
    if key.size is not 0:
        print(key.get_contents_as_string())
