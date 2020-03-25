from amo_service import AMOService
from multiprocessing import Process, Queue
import requests


async def polling_from_explorer(q, blockchain_endpoint):
    while True:
        requests.get('{}/tx_search'.format(blockchain_endpoint), params={}, timeout=60)


class GrantService:
    def __init__(self, amo):
        self.amo = AMOService(**amo)
        self.polling_service = None

    def run(self, polling_func):
        request_queue = Queue()

        self.polling_service = Process(target=polling_func, args=(request_queue,))
        self.polling_service.start()

        while True:
            request = request_queue.get()
            grant_tx = self.amo.grant_parcel(**request)
            self.amo.broadcast_tx(grant_tx)

    def terminate(self):
        if self.polling_service is not None and self.polling_service.is_alive():
            self.polling_service.terminate()
