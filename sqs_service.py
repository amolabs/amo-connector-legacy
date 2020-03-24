import json

import boto3


class SQSService:
    def __init__(self, credential: dict, sqs: dict):
        self.sqs = boto3.resource('sqs', **credential)
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Queue
        self.queue = self.sqs.Queue(sqs['url'])
        self.cache = dict()

    def polling(self) -> [dict]:
        messages = self.queue.receive_messages(
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )

        payloads = []
        for message in messages:
            body = json.loads(message.body)
            payload = body['responsePayload']
            payloads.extend(payload)

        return payloads
