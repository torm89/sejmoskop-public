import json
from abc import ABC, abstractmethod
from typing import Dict

from opensearchpy import OpenSearch

from processing.models.dao import Dao, D, T
from processing.providers.aws import AwsProvider
from processing.utils.utils import chunks


class DaoAwsOpensearch(Dao[T, D], ABC):

    def __init__(self):
        self.provider = AwsProvider()

        self.initialize()

    @abstractmethod
    def initialize(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def opensearch_endpoint(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def opensearch_index(self, tag: T) -> str:
        raise NotImplementedError

    @abstractmethod
    def document_id(self, tag: T, data: Dict) -> str:
        raise NotImplementedError

    @property
    def client(self) -> OpenSearch:
        return self.provider.client_opensearch(host=self.opensearch_endpoint)

    def save(self, data: D) -> None:
        for chunk in chunks(data.data, 100):
            payload = []

            for doc in chunk:
                payload += [
                    json.dumps({
                        "update": {
                            "_index": self.opensearch_index(tag=data.tag),
                            "_id": self.document_id(tag=data.tag, data=doc)
                        }
                    }),
                    json.dumps({"doc": doc, "doc_as_upsert": True})
                ]

            self.client.bulk("\n".join(payload))
