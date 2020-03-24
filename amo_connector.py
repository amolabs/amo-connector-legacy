import argparse
import sys
from pathlib import Path

from loguru import logger
from requests import HTTPError
from yaml import load, FullLoader

from amo_service import AMOService
from s3_service import S3Service
from sqs_service import SQSService


class AMOConnector:
    def __init__(self, config_dir: str):
        config = self._get_config(config_dir)
        aws = config['aws']

        self.sqs = SQSService(aws['credential'], aws['sqs'])
        self.s3 = S3Service(aws['credential'], aws['s3'])
        self.amo = AMOService(**config['amo'])

    @staticmethod
    def _get_config(config_dir: str):
        with open(Path(config_dir).expanduser() / 'config.yml', 'r') as stream:
            config = load(stream, Loader=FullLoader)
        return config

    def run(self):
        while True:
            parcels = self.sqs.polling()
            for parcel in parcels:
                bucket, key = parcel['bucket'], parcel['key']
                try:
                    content = self.s3.get_content(bucket, key)

                    parcel_id, custody = self.amo.upload_parcel(content)

                    register_tx = self.amo.register_parcel(parcel_id, custody)
                    tx_result = self.amo.broadcast_tx(register_tx)
                    logger.debug('{key} -> {result}', key=key, result=tx_result)

                    self.s3.add_tag(bucket, key, parcel_id)
                    logger.info('{key} -> {parcel_id}', key=key, parcel_id=parcel_id)
                except HTTPError as e:
                    logger.error('{key} occurs {error} with {content}',
                                 key=key, error=e, content=e.response.content)
                except Exception as e:
                    logger.exception('{key} failed by {error}', key=key, error=e)


if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stdout,
               format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                      "<level>{level: <8}</level> | <level>{message}</level>")

    parser = argparse.ArgumentParser()
    parser.add_argument('--config_dir', type=str, default='~/.amo-connector')

    args = parser.parse_args()

    connector = AMOConnector(args.config_dir)
    connector.run()
