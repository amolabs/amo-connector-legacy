import argparse
import stat
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger
from requests import HTTPError
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from yaml import load, FullLoader

from amo_service import AMOService
from s3_service import S3Service
from sqs_service import SQSService


def get_config(config_dir: str):
    path = Path(config_dir).expanduser() / 'amo-connector.yml'
    with open(path, 'r') as stream:
        permissions = path.stat().st_mode
        owner_permissions = stat.S_IRUSR | stat.S_IWUSR
        if permissions ^ owner_permissions != 0:
            raise PermissionError(
                "Unprotected config file. Permissions {} for 'amo-connector.yml' are too open".format(
                    stat.filemode(path.stat().st_mode)))

        return load(stream, Loader=FullLoader)


Base = declarative_base()


class ParcelLog(Base):
    __tablename__ = 'parcel_log'

    parcel_id = Column(String(72), primary_key=True)
    bucket_name = Column(String(256))
    object_key = Column(String(512))
    created_at = Column(DateTime, default=datetime.now)


class AMOConnector:
    def __init__(self, aws, amo, db):
        self.sqs = SQSService(aws['credential'], aws['sqs'])
        self.s3 = S3Service(aws['credential'], aws.get('s3', {}))
        self.amo = AMOService(**amo)
        self._load_database(db)

    def _load_database(self, db):
        self.engine = create_engine(db['host'])
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def save_result(self, parcel_id, bucket_name, object_key):
        result = ParcelLog(
            parcel_id=parcel_id,
            bucket_name=bucket_name,
            object_key=object_key
        )
        self.session.add(result)
        self.session.commit()

    def run(self):
        while True:
            parcels = self.sqs.polling()
            for parcel in parcels:
                bucket, key = parcel['bucket'], parcel['key']
                try:
                    owned_tags = self.s3.get_tags(bucket, key)
                    if 'parcel_id' in owned_tags:
                        logger.info('{key} registered parcel with {parcel_id}',
                                    key=key, parcel_id=owned_tags['parcel_id'])
                        continue

                    content = self.s3.get_content(bucket, key)

                    parcel_id, custody = self.amo.upload_parcel(content)

                    register_tx = self.amo.register_parcel(parcel_id, custody)
                    tx_result = self.amo.broadcast_tx(register_tx)
                    logger.debug('{key} -> {result}', key=key, result=tx_result)

                    self.s3.add_tag(bucket, key, parcel_id)
                    self.save_result(parcel_id, bucket, key)
                    logger.info('{key} -> {parcel_id}', key=key, parcel_id=parcel_id)
                except HTTPError as e:
                    logger.error('{key} occurs {error} with {content}',
                                 key=key, error=e, content=e.response.content)
                except Exception as e:
                    logger.exception('{key} failed by {error}', key=key, error=e)

    def __exit__(self, *args, **kwargs):
        self.session.close()


if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stdout,
               format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                      "<level>{level: <8}</level> | <level>{message}</level>")

    parser = argparse.ArgumentParser()
    parser.add_argument('--config_dir', type=str, default='~/.amo-connector')

    parsed_args = parser.parse_args()

    config = get_config(parsed_args.config_dir)

    connector = AMOConnector(**config)
    connector.run()
