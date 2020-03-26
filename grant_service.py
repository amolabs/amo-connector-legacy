from multiprocessing import Process, Queue

import requests

from amo_service import AMOService


def polling_from_explorer(q, explorer_endpoint):
    requests.get('{}/tx_search'.format(explorer_endpoint), params={}, timeout=60)


class RequestTx:
    def __init__(self, tx: dict):
        payload = tx['payload']
        signature = tx['signature']

        self.parcel_id = payload['target']
        self.payment = payload['payment']
        self.pubKey = signature['pubKey']
        self.grantee = tx['sender']

    def is_valid(self) -> bool:
        if len(self.parcel_id) != (64 + 8):
            return False
        if len(self.pubKey) != 130:
            return False
        if not (int(self.payment) > 0):
            return False
        return True


class GrantService:
    def __init__(self, amo, explorer_endpoint):
        self.amo = AMOService(**amo)
        self.polling_service = None
        self.explorer_endpoint = explorer_endpoint

    def run(self, polling_func):
        request_queue = Queue()

        self.polling_service = Process(target=polling_func, args=(request_queue, self.explorer_endpoint))
        self.polling_service.start()

        while True:
            request = request_queue.get()
            try:
                tx = RequestTx(request)

                if not tx.is_valid():
                    continue

                custody = self.amo.query_parcel(tx.parcel_id)['custody']

                grant_custody = self.amo.get_grant_custody(custody, tx.pubKey)

                grant_tx = self.amo.grant_parcel(tx.parcel_id, tx.grantee, grant_custody)
                self.amo.broadcast_tx(grant_tx)
            except Exception as e:
                continue

    def terminate(self):
        if self.polling_service is not None and self.polling_service.is_alive():
            self.polling_service.terminate()
