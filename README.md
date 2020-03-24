# AMO Connector

- Receive file creation event from AWS SQS
- Download file content from AWS S3
- Upload parcel to AMO storage
- Register parcel to AMO blockchain

## Config

Config file 

```yaml
amo:
    blockchain_endpoint: <AMO blockchain RPC endpoint>
    stroage_endpoint: <AMO storage endpoint>
    private_key: <Hex encoded 32 bytes>
aws:
    credential:
      aws_access_key_id: <ACCESS_KEY>
      aws_secret_access_key: <SERECT_KEY>
      region_name: <REGION>
    sqs:
      url: <QUEUE_URL>
```

## Usage
`python3 amo_connector.py --config_dir <Directory of config file>`
