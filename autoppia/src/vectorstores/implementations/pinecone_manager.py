import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

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

logger = logging.getLogger(__name__)


class PineconeManager(VectorStoreInterface):
    """Pinecone vector store implementation.
    
    Manages vector store operations using Pinecone with improved performance,
    error handling, and resource management.
    """
    
    # File type to loader mapping for better performance
    LOADER_MAP = {
        'txt': TextLoader,
        'pdf': PyPDFLoader,
        'docx': Docx2txtLoader,
        'csv': CSVLoader,
    }
    
    # Default text splitter configuration
    DEFAULT_CHUNK_SIZE = 1500
    DEFAULT_CHUNK_OVERLAP = 200

    def __init__(self, api_key: str, index_name: str, embedding_api_key: str,
                 chunk_size: int = DEFAULT_CHUNK_SIZE, 
                 chunk_overlap: int = DEFAULT_CHUNK_OVERLAP):
        """Initialize Pinecone vector store manager.
        
        Args:
            api_key: Pinecone API key
            index_name: Name of the Pinecone index
            embedding_api_key: OpenAI API key for embeddings
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between text chunks
        """
        self.api_key = api_key
        self.index_name = index_name
        self.embedding_api_key = embedding_api_key
        
        # Initialize embeddings once and reuse
        self.embeddings = OpenAIEmbeddings(api_key=embedding_api_key)
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.api_key)
        
        # Initialize text splitter with configurable parameters
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Initialize S3 manager
        self.s3_manager = S3Manager()
        
        # Create or get collection
        self.pcvs = self.get_or_create_collection()
        
        logger.info(f"PineconeManager initialized for index: {index_name}")

    def get_or_create_collection(self) -> PineconeVectorStore:
        """Get existing Pinecone index or create new one with error handling.
        
        Returns:
            PineconeVectorStore: Vector store instance
            
        Raises:
            Exception: If index creation or retrieval fails
        """
        try:
            existing_indexes = self.pc.list_indexes().names()
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    self.index_name,
                    dimension=1536,
                    metric="cosine",
                    spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
                )
                logger.info(f"Successfully created index: {self.index_name}")
            else:
                logger.info(f"Using existing index: {self.index_name}")
                
            # Construct vector store directly with API key to avoid env var dependency
            return PineconeVectorStore(
                embedding=self.embeddings,
                pinecone_api_key=self.api_key,
                index_name=self.index_name,
            )
            
        except Exception as e:
            logger.error(f"Failed to get or create collection: {e}")
            raise


    def add_document(self, file_path: str, filter: Optional[Dict[str, Any]] = None) -> None:
        """Add a document to the vector store with optimized processing.
        
        Args:
            file_path: Path to the document file
            filter: Optional metadata filter for the document
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported
            Exception: If document processing fails
        """
        if filter is None:
            filter = {"chat_session": 1}
            
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            logger.info(f"Processing document: {Path(file_path).name}")
            
            # Load document
            documents = self.load(file_path)
            if not documents:
                logger.warning(f"No content loaded from {file_path}")
                return
                
            # Split documents using pre-configured splitter
            docs = self.text_splitter.split_documents(documents)
            logger.info(f"Split document into {len(docs)} chunks")
            
            # Prepare texts and metadata efficiently
            texts = [doc.page_content for doc in docs]
            metadatas = [
                {**filter, "chunk_index": i, "file_path": file_path}
                for i in range(len(docs))
            ]
            
            # Add to vector store
            self.pcvs.add_texts(texts=texts, metadatas=metadatas)
            logger.info(f"Successfully added document to vector store")
            
        except Exception as e:
            logger.error(f"Failed to add document {file_path}: {e}")
            raise
    def delete_document(self, filter: Dict[str, Any]) -> None:
        """Delete vectors matching a metadata filter from the index.
        
        Args:
            filter: Metadata filter to match vectors for deletion
            
        Raises:
            Exception: If deletion fails
        """
        try:
            pinecone_index = PineconeVectorStore.get_pinecone_index(
                index_name=self.index_name,
                pinecone_api_key=self.api_key,
            )
            pinecone_index.delete(filter=filter or {})
            logger.info(f"Successfully deleted vectors matching filter: {filter}")
        except Exception as e:
            logger.error(f"Failed to delete vectors with filter {filter}: {e}")
            raise

    def get_context(self, query: str, filter: Optional[Dict[str, Any]] = None, 
                   k: int = 4) -> str:
        """Get relevant context based on query with optimized search.
        
        Args:
            query: Search query
            filter: Optional metadata filter for search
            k: Number of similar documents to retrieve
            
        Returns:
            Formatted context string
            
        Raises:
            Exception: If context retrieval fails
        """
        try:
            context = self.pcvs.similarity_search(
                query, 
                filter=filter or {},
                k=k
            )
            
            if not context:
                return "No relevant context found for your query."
            
            # Format context more efficiently
            context_text = "\n\n".join([doc.page_content for doc in context])
            
            template = f"""Following Context is data from documents that user wants to know about.
If the user sends a greeting such as 'hi', 'hello' and 'good morning', don't make other answers, just send the user greeting and ask what you can help.

Context: {context_text}

Question: {query}"""
            
            logger.info(f"Retrieved {len(context)} documents for query")
            return template
            
        except Exception as e:
            logger.error(f"Failed to get context for query: {e}")
            raise

    def load(self, file_path: str) -> List[Any]:
        """Load document from file path using appropriate loader.
        
        Supports multiple file types including txt, pdf, docx, and csv.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of loaded documents
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is not supported
            Exception: If document loading fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_type = self.get_file_type(file_path)
        
        if file_type not in self.LOADER_MAP:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        try:
            loader_class = self.LOADER_MAP[file_type]
            loader = loader_class(file_path)
            documents = loader.load()
            
            logger.info(f"Loaded {len(documents)} pages from {file_type} file: {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to load {file_type} file {file_path}: {e}")
            raise

    @staticmethod
    def get_file_type(file_path: str) -> str:
        """Get file extension from path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File extension in lowercase (without the dot)
        """
        return Path(file_path).suffix[1:].lower()
