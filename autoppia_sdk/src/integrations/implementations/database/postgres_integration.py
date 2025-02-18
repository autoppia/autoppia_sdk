from typing import Optional
from autoppia_sdk.src.integrations.implementations.database.interface import DatabaseIntegration
from autoppia_sdk.src.integrations.config import IntegrationConfig
from autoppia_sdk.src.integrations.implementations.base import Integration
import psycopg2


class PostgresIntegration(DatabaseIntegration, Integration):
    """PostgreSQL database integration implementation.
    
    This class provides functionality to interact with PostgreSQL databases,
    implementing both DatabaseIntegration and Integration interfaces.
    """

    def __init__(self, integration_config: IntegrationConfig):
        """Initialize PostgreSQL integration with configuration parameters.
        
        Args:
            integration_config (IntegrationConfig): Configuration object containing
                connection parameters including:
                - host: Database server hostname
                - user: Database username
                - port: Database port number
                - dbname: Database name
                - password: Database password
        """
        self.integration_config = integration_config
        self.host = integration_config.attributes.get("host")
        self.user = integration_config.attributes.get("user")
        self.port = integration_config.attributes.get("port")
        self.dbname = integration_config.attributes.get("dbname")
        self._password = integration_config.attributes.get("password")

    def execute_sql(
        self,
        sql: str,
    ) -> Optional[str]:
        """Execute SQL query on PostgreSQL database and return results.
        
        Args:
            sql (str): SQL query to execute
            
        Returns:
            Optional[str]: Query results if successful, None if an error occurs
            
        Note:
            The connection is automatically closed after query execution,
            regardless of success or failure.
        """
        try:
            conn = psycopg2.connect(host=self.host, user=self.user, password=self._password, dbname=self.dbname)
            cursor = conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()

            return results
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    