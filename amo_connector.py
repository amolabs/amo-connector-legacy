import argparse
import os

from yaml import load, FullLoader

from sqs_service import SQSService
from s3_service import S3Service
from amo_service import AMOService


class AMOConnector:
    def __init__(self, config_dir: str):
        config = self._get_config(config_dir)
        aws = config['aws']

        self.sqs = SQSService(aws['credential'], aws['sqs'])
        self.s3 = S3Service(aws['credential'], aws['s3'])
        self.amo = AMOService(**config['amo'])

    @staticmethod
    def _get_config(config_dir: str):
        with open(os.path.join(config_dir, 'config.yml'), 'r') as stream:
            config = load(stream, Loader=FullLoader)
        return config

    def run(self):
        while True:
            parcels = self.sqs.polling()
            # TODO multi thread
            for parcel in parcels:
                bucket, key = parcel['bucket'], parcel['key']
                content = self.s3.get_content(bucket, key)
                parcel_id, custody = self.amo.upload_parcel(content)
                register_tx = self.amo.register_parcel(parcel_id, custody)
                res = self.amo.broadcast_tx(register_tx)
                self.s3.add_tag(bucket, key, parcel_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_dir', type=str, default=os.path.join(os.path.expanduser('~'), '.amo-connector'))

    args = parser.parse_args()

    connector = AMOConnector(args.config_dir)
    connector.run()
