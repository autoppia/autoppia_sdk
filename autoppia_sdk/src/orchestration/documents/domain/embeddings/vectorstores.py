# from abc import ABC, abstractmethod
# from typing import List

# from autoppia_agentic_framework.src.core.documents.classes import Document


# class VectorStoreProviders:
#     CHROMA_DB = "chroma"


# class AbstractVectorStoreWrapper(ABC):
#     @abstractmethod
#     def getOrCreateCollection(self, collectionName):
#         pass

#     @abstractmethod
#     def deleteCollection(self, collectionName):
#         pass

#     @abstractmethod
#     def listCollections(self):
#         pass

#     @abstractmethod
#     def addDocuments(self, documents: List[Document]):
#         pass

#     @abstractmethod
#     def similaritySearch(self, query: str, k: int = 4):
#         pass
