"""
Document Class is in charge of storing data-medatada pairs. Data is basically text and metada all necesary information to understand the data.
Source, timestamp etc

Document List is to serialize documents and to transform aggregates.

As document modules sometimes use langchain functionality there are functions to transform from lanchain documents to our native Document Class and viceversa.
"""


from typing import List

from autoppia_agentic_framework.src.shared.utils.dao.serializables import JSONSerializable


class Document(JSONSerializable):
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata

    def __str__(self):
        return self.toJSON()

    def setId(self, id):
        self._id = id

    def saveInDocumentsBD():
        pass

    @classmethod
    def fromLangchainDocument(cls, langchain_doc):
        return cls(
            page_content=langchain_doc.page_content,
            metadata=langchain_doc.metadata,
        )


class DocumentList(JSONSerializable):
    def __init__(self, documents: List[Document]):
        self.documents = documents

    def __str__(self):
        return self.toJSON()

    def build_from_text(self):
        pass

    @staticmethod
    def fromLangchainDocuments(langchain_docs) -> List[Document]:
        return [Document.fromLangchainDocument(doc) for doc in langchain_docs]

    @classmethod
    def fromStringList(cls, stringList, metadata):
        documents = []
        for string in stringList:
            documents.append(Document(string, metadata))
        return documents
