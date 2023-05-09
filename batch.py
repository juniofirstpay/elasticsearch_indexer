#python native dependencies
import queue
import threading
import secrets
import time

#external package
import structlog

#python native dependencies
from datetime import datetime

#external package
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class ESBatchWriter:

    def __init__(self, config, default_index, debug=False):
        self.__debug = debug
        self._default_index = default_index
        self._queue = queue.Queue(maxsize=1000000)
        self._items = []
        self._elasticsearch = Elasticsearch(**config)
        self._logger = structlog.get_logger(__name__)

    def start(self):
        self._thread = threading.Thread(
            target=self.worker, daemon=True).start()

    def worker(self):
        self._logger.info("Worker Loop Running")
        should_write = False
        while True:
            stop = False
            while stop == False and len(self._items) < 100:
                try:
                    self._items.append(self._queue.get(block=True, timeout=3))
                    stop = False
                    
                    self.__debug and self._logger.debug("Queue got an item")
                except queue.Empty as e:
                    
                    self.__debug and self._logger.debug("Queue raised an empty exception")
                    
                    if len(self._items) == 0:
                        
                        self.__debug and self._logger.debug("Worker going to sleep for 5 seconds")
                        
                        time.sleep(5)
                    else:
                        should_write = True
                    stop = True
                    pass

            if len(self._items) >= 100 or (should_write and len(self._items) > 0):
                self.__debug and self._logger.debug("Queue has more that 100 items")
                
                mapped_items = self._items
                self._logger.debug(mapped_items)
                bulk(self._elasticsearch, mapped_items,
                     index=self._default_index)
                
                self.__debug and self._logger.debug("Items flushed to elastic search")
                
                self._items = []
                should_write = False

    def write(self, group: str, data: "str"):
        try:
            self._queue.put(
                {
                    "_id": secrets.token_bytes(32).hex(),
                    "timestamp": datetime.utcnow().isoformat(),
                    "group": group,
                    "data": data,
                },
                block=True,
                timeout=100,
            )
        except queue.Full:
            pass

    def index(self, *args, **kwargs):
        self._elasticsearch.index(*args, **kwargs)
