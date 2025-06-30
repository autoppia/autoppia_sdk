from abc import ABC, abstractmethod


class VectorStoreInterface(ABC):
    """Interface for vector store implementations.
    
    Defines the required methods that all vector store implementations must provide.
    """

    @abstractmethod
    def get_or_create_collection(self, collection_name):
        """Get an existing collection or create a new one if it doesn't exist.
        
        Args:
            collection_name (str): Name of the collection to get or create
            
        Returns:
            Any: The vector store collection instance
        """
        pass

    @abstractmethod
    def add_document(self, document):
        """Add a document to the vector store.
        
        Args:
            document: Document to be added to the vector store
        """
        pass

    @abstractmethod
    def get_context(self, query):
        """Retrieve relevant context based on a query.
        
        Args:
            query (str): The search query
            
        Returns:
            str: Retrieved context based on the query
        """
        pass
