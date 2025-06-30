from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class DatabaseIntegration(ABC):
    """Abstract base class for database integrations.

    This class defines the interface for database operations that must be implemented
    by concrete database integration classes.
    """

    @abstractmethod
    def execute_sql(
        self,
        sql: str,
    ):
        """Execute a SQL query on the database.

        Args:
            sql (str): The SQL query to execute.

        Returns:
            Any: The result of the SQL query execution. The specific return type
                 depends on the implementing class and the query type.

        Raises:
            Exception: Implementation-specific exceptions may be raised based on
                      the concrete database integration.
        """
        pass
