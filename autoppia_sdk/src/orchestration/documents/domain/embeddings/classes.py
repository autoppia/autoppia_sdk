# from typing import List, Set

# from autoppia_agentic_framework.src.core.documents.classes import Document
# from autoppia_agentic_framework.src.core.documents.embeddings.chromadb.chromadb import ChromaWrapper
# from autoppia_agentic_framework.src.core.documents.embeddings.vectorstores import (
#     AbstractVectorStoreWrapper,
#     VectorStoreProviders,
# )


# class DocumentEmbedder:
#     VECTOR_STORES_WRAPPERS = {VectorStoreProviders.CHROMA_DB: ChromaWrapper()}

#     def __init__(self, vectorStoreProvider=VectorStoreProviders.CHROMA_DB) -> None:
#         self.vectorStoreProvider = vectorStoreProvider
#         self.vectorStore: AbstractVectorStoreWrapper = (
#             DocumentEmbedder.VECTOR_STORES_WRAPPERS[self.vectorStoreProvider]
#         )

#         # Retrieve already embedded document IDs from the VectorStore
#         self.alreadyEmbeddedDocumentIds: Set[
#             str
#         ] = self.vectorStore.getEmbeddedDocumentIds()

#     def checkIfAlreadyEmbedded(self, documentId: str) -> bool:
#         return documentId in self.alreadyEmbeddedDocumentIds

#     def embed(self, documents: List[Document], force=False):
#         newDocuments = []
#         for document in documents:
#             if self.checkIfAlreadyEmbedded(document._id) or force:
#                 newDocuments.append(document)

#         return self.vectorStore.addDocuments(newDocuments)

#     # def embedAndLink(self, documents: List[Document], documentDatabaseManager: DocumentDatabaseManager):
#     #     # Embed the documents and get the references/ids of the embeddings.
#     #     embedding_references = self.embed(documents)

#     #     # Loop over documents and link each one to its embedding
#     #     for document, embedding_reference in zip(documents, embedding_references):
#     #         documentDatabaseManager.linkDocumentToEmbedding(document['_id'], embedding_reference)

#     def list(self):
#         return self.vectorStore.listCollections()
