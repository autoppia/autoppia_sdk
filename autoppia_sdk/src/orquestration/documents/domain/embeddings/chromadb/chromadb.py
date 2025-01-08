# import os
# from datetime import datetime

# from chromadb import PersistentClient
# from chromadb.api import Collection
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import _import_chroma

# from autoppia_agentic_framework.src.core.documents.embeddings.vectorstores import (
#     AbstractVectorStoreWrapper,
# )

# _import_chroma()


# class ChromaWrapper(AbstractVectorStoreWrapper):
#     DEFAULT_ARP_CHROMADB_COLLECTION_NAME = "default"

#     def __init__(
#         self, collectionName=DEFAULT_ARP_CHROMADB_COLLECTION_NAME, embeddings=None
#     ):
#         self.collectionName = collectionName
#         self.persistPath = "C:\\proyectos\\autoppia\\autoppia_AI\\"
#         if embeddings is None:
#             self.embeddings = OpenAIEmbeddings(
#                 openai_api_key=os.environ["OPENAI_API_KEY"]
#             )
#         self.client = PersistentClient(path=self.persistPath)
#         self.collectionName: str = collectionName
#         self.collection: Collection = self.getOrCreateCollection(collectionName)
#         # self.langchainChroma = LangchainChroma(
#         #     collection_name=collectionName,
#         #     embedding_function=self.embeddings,
#         #     persist_directory=self.persistPath,
#         # )

#     def listCollections(self):
#         return self.client.list_collections()

#     def getOrCreateCollection(self, collectionName=None) -> Collection:
#         collectionName = collectionName if collectionName else self.collectionName
#         return self.client.get_or_create_collection(name=self.collectionName)

#     def deleteCollection(self, collectionName=None):
#         collectionName = collectionName if collectionName else self.collectionName
#         return self.client.delete_collection(name=self.collectionName)

#     def getEmbeddedDocumentIds(self):
#         return self.collection.get(include=["documents"])

#     # def addDocuments(self, documents: List[Document]):
#     #     kargs: dict = {}
#     #     for doc in documents:
#     #         if doc.metadata is None:
#     #             doc.metadata = {}
#     #         doc.metadata["timestamp"] = self._getCurrentTimestamp()
#     #         if "id" in doc.metadata:
#     #             if "ids" not in kargs:
#     #                 kargs["ids"] = []
#     #             kargs["ids"].append(doc.metadata["id"])
#     #     return self.langchainChroma.add_documents(documents, **kargs)

#     def _getCurrentTimestamp(self):
#         return datetime.now().isoformat()

#     def similaritySearch(
#         self, query: str, k: int = 4, filter=None, metadataFilter=None
#     ):
#         return self.langchainChroma.similarity_search(query, k=k)

#     def manualQuery(self, queries, k=5, where=None, where_document=None):
#         return self.client.collection.query(
#             query_texts=queries, n_results=k, where=where, where_document=where_document
#         )

#     def similaritySearchByEmbedding(self, embedding, k: int = 4):
#         # Assuming LangchainChroma has a method for similarity search by embedding
#         return self.langchainChroma.similarity_search_by_vector(embedding, k=k)
