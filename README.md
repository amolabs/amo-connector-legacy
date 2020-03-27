# AMO Connector

- Receive file creation event from AWS SQS
    - AMO connector supposes events are created by AWS Lambda triggered by S3.
    - Message from SQS must contains `bucket` and `key` in `responsePayload`.
- Download file content from AWS S3
- Upload parcel to AMO storage
    - AMO connector encrypts data from above step with custody.
- Register parcel to AMO blockchain

## Configuration

AMO connector uses [yaml](https://github.com/yaml/pyyaml) for configuration

### amo-connector.yml

```yaml
amo:
    blockchain_endpoint: <AMO_BLOCKCHAIN_RPC_ENDPOINT>
    stroage_endpoint: <AMO_STORAGE_ENDPOINT>
    private_key: <HEX_ENCODED_32_BYTES>
aws:
    credential:
      aws_access_key_id: <ACCESS_KEY>
      aws_secret_access_key: <SERECT_KEY>
      region_name: <REGION>
    sqs:
      url: <QUEUE_URL>
db:
    host: mysql+pymysql://<USER>:<PASSWORD>@localhost:3306/amo-storage
```

AMO connector needs those permissions:
- S3, Full access
- SQS, Full: Read

## Run

### Standalone

```bash
$ python3 amo_connector.py --config_dir <Directory of config file>
```

### Run with AMO storage

```bash
$ sudo sh ./run.sh
``` 

If you execute this command, it will download AMO storage and run docker-compose

Your config directory should be like

```
├── config
│   ├── amo-connector.yml
│   ├── config.ini
│   └── key.json
```

`config.ini` and `key.json` are config files of AMO storage.
Check out this [page](https://github.com/amolabs/amo-storage/blob/master/README.md#configurations).

Also, you need to export below environment values. Or you can create `.env` file in
same path of AMO connector's docker-compose.yml.

```
PORT=5000
CONFIG_DIR=config

MYSQL_ROOT_PASSWORD=<ROOT_PASSWORD>
MYSQL_USER=<USER>
MYSQL_PASSWORD=<PASSOWRD>
```
