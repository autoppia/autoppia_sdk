from abc import ABC, abstractmethod


class VectorStoreInterface(ABC):
    @abstractmethod
    def get_or_create_collection(self, collection_name):
        pass

    @abstractmethod
    def add_document(self, document):
        pass

    @abstractmethod
    def get_context(self, query):
        pass
