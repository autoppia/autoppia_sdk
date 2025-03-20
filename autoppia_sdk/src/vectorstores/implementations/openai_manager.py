from openai import OpenAI

from autoppia_sdk.src.vectorstores.interface import VectorStoreInterface
from autoppia_sdk.src.vectorstores.implementations.s3_manager import S3Manager


class OpenAIManager(VectorStoreInterface):
    """OpenAI vector store implementation.
    
    Manages vector store operations using OpenAI's API.
    """

    def __init__(self, index_name: str, vector_store_id: str = None):
        """Initialize OpenAI vector store manager.
        
        Args:
            index_name (str): Name of the vector store index
            vector_store_id (str, optional): ID of existing vector store
        """
        self.vector_store_id = vector_store_id
        self.client = OpenAI()
        self.s3_manager = S3Manager()
        self.index_name = index_name

    def get_or_create_collection(self):
        """Get existing vector store or create new one.
        
        Returns:
            object: OpenAI vector store instance
        """
        if self.vector_store_id:
            vector_store = self.client.beta.vector_stores.retrieve(
                vector_store_id=self.vector_store_id
            )
            return vector_store
        else:
            return self.client.beta.vector_stores.create(name=self.index_name)

    def add_document(self, file_path):
        """Add a document to the vector store.
        
        Args:
            file_path (str): Path to the document file
        """
        # Get or create the vector store if not already set
        if not self.vector_store_id:
            vector_store = self.get_or_create_collection()
            self.vector_store_id = vector_store.id
        
        # Upload the file to OpenAI
        try:
            with open(file_path, 'rb') as file:
                file_upload = self.client.files.create(
                    file=file,
                    purpose="assistants"
                )
                file_id = file_upload.id
                
                # Add the file to the vector store
                self.client.beta.vector_stores.files.create(
                    vector_store_id=self.vector_store_id, 
                    file_id=file_id
                )
                
                return file_id
        except Exception as e:
            raise Exception(f"Error adding document to OpenAI vector store: {str(e)}")

    def get_context(self):
        pass

    def get_files(self, vector_store_id: str):
        """List files in a vector store.
        
        Args:
            vector_store_id (str): ID of the vector store
            
        Returns:
            list: List of files in the vector store
        """
        vector_store_files = self.client.beta.vector_stores.files.list(
            vector_store_id=vector_store_id
        )

        return vector_store_files

    def add_file_batch(self, vector_store_id: str, file_ids: list):
        """Add multiple files to the vector store.
        
        Args:
            vector_store_id (str): ID of the vector store
            file_ids (list): List of file IDs to add
        """
        self.client.beta.vector_stores.file_batches.create(
            vector_store_id=vector_store_id, file_ids=file_ids
        )
