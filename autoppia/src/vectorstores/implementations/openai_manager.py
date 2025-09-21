from openai import OpenAI

from autoppia.src.vectorstores.interface import VectorStoreInterface
from autoppia.src.vectorstores.implementations.s3_manager import S3Manager


class OpenAIManager(VectorStoreInterface):
    """OpenAI vector store implementation.
    
    Manages vector store operations using OpenAI's API.
    """

    def __init__(self, api_key: str, index_name: str, vector_store_id: str = None):
        """Initialize OpenAI vector store manager.
        
        Args:
            api_key (str): OpenAI API key
            index_name (str): Name of the vector store index
            vector_store_id (str, optional): ID of existing vector store
        """
        self.vector_store_id = vector_store_id
        self.client = OpenAI(api_key=api_key)
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

    def delete_document(self, file_id: str):
        """Delete a file from the vector store (and optionally from OpenAI storage)."""
        if not self.vector_store_id or not file_id:
            return
        try:
            self.client.beta.vector_stores.files.delete(
                vector_store_id=self.vector_store_id,
                file_id=file_id,
            )
            # Best-effort cleanup of file storage
            try:
                self.client.files.delete(file_id=file_id)
            except Exception:
                pass
        except Exception:
            pass

    def get_context(self, query: str) -> str:
        """Search the vector store using file_search via Responses API and return text context."""
        if not self.vector_store_id:
            return ""
        try:
            response = self.client.responses.create(
                model="gpt-4o-mini",
                input=query,
                tools=[{"type": "file_search"}],
                search={"vector_store_ids": [self.vector_store_id]},
            )
            text = getattr(response, "output_text", None)
            if text:
                return text
            outputs = getattr(response, "output", [])
            parts = []
            for item in outputs:
                for content in getattr(item, "content", []):
                    value = getattr(getattr(content, "text", None), "value", None)
                    if value:
                        parts.append(value)
            return "\n".join(parts)
        except Exception:
            return ""

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
