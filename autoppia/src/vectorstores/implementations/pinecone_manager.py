import os

from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone as PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone

from autoppia.src.vectorstores.interface import VectorStoreInterface
from autoppia.src.vectorstores.implementations.s3_manager import S3Manager


class PineconeManager(VectorStoreInterface):
    """Pinecone vector store implementation.
    
    Manages vector store operations using Pinecone, including document loading,
    chunking, and similarity search capabilities.
    """

    def __init__(self, api_key: str, index_name: str):
        """Initialize Pinecone vector store manager.
        
        Args:
            api_key (str): Pinecone API key
            index_name (str): Name of the Pinecone index
        """
        self.embeddings = OpenAIEmbeddings()
        self.index_name = index_name
        self.api_key = api_key
        self.pc = Pinecone(api_key=self.api_key)
        self.pcvs = self.get_or_create_collection(self.index_name)
        self.s3_manager = S3Manager()

    def get_or_create_collection(self, index_name):
        """Get existing Pinecone index or create new one.
        
        Args:
            index_name (str): Name of the index
            
        Returns:
            PineconeVectorStore: Vector store instance
        """
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(index_name, dimension=1536, metric="cosine", spec={"serverless": {"cloud": "aws", "region": "us-east-1"}})
        return PineconeVectorStore.from_existing_index(self.index_name, self.embeddings)

    def add_document(self, file_path, filter={"chat_session": 1}):
        """Add a document to the vector store.
        
        Args:
            file_path (str): Path to the document file
            filter (dict, optional): Metadata filter for the document
        """
        # tempFilePath = "temp/file.pdf"
        # self.s3_manager.downloadFile(document.s3_object_key, tempFilePath)
        documents = self.load(file_path)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500, chunk_overlap=200
        )
        docs = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()

        texts = [d.page_content for d in docs]
        metadatas = [filter for d in docs]

        # Save Vector DB in pinecone
        PineconeVectorStore.from_texts(
            texts, embeddings, metadatas=metadatas, index_name=self.index_name
        )
        # PineconeVectorStore.from_documents(docs, embeddings, index_name=self.index_name)

    def get_context(self, query, filter=None):
        """Get relevant context based on query.
        
        Args:
            query (str): Search query
            filter (dict): Metadata filter for search
            
        Returns:
            str: Template with context and query
        """
        if filter:
            context = self.pcvs.similarity_search(query, filter=filter)
        else:
            context = self.pcvs.similarity_search(query)

        template = f"""
            Following Context is data of PDF that user want to know about information of.
            If the user sends a greeting such as 'hi','hello' and 'good morning', don't make other answers, just send the user greeting and ask what you can help.
            Context:{context}
            Question: {query}
            """
        return template

    def load(self, file_path):
        """Load document from file path.
        
        Supports multiple file types including txt, pdf, docx, and csv.
        
        Args:
            file_path (str): Path to the document file
            
        Returns:
            list: Loaded documents
        """
        file_type = self.get_file_type(file_path)

        if file_type == "txt":
            # Text loader for txt files
            loader = TextLoader(file_path)
            return loader.load()
        elif file_type == "pdf":
            # PDF loader for pdf files
            loader = PyPDFLoader(file_path)
            return loader.load()
        elif file_type == "docx":
            # Word loader for docx files
            loader = Docx2txtLoader(file_path)
            return loader.load()
        elif file_type == "csv":
            # CSV loader for csv files
            loader = CSVLoader(file_path)
            return loader.load()
        else:
            print(f"{file_type} is not supported.")
            return

    @staticmethod
    def get_file_type(file_path):
        """Get file extension from path.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: File extension without dot
        """
        _, ext = os.path.splitext(file_path)
        return ext[1:].lower()
