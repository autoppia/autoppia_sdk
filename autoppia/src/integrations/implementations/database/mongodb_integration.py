from typing import Optional, Any
from autoppia.src.integrations.implementations.database.interface import DatabaseIntegration
from autoppia.src.integrations.config import IntegrationConfig
from autoppia.src.integrations.implementations.base import Integration
from pymongo import MongoClient


class MongoDBIntegration(DatabaseIntegration, Integration):
    """MongoDB database integration implementation.
    
    Provides basic connection and query execution for MongoDB.
    Expects attributes: uri (or host/port), database, and optional username/password.
    """

    def __init__(self, integration_config: IntegrationConfig):
        self.integration_config = integration_config
        attrs = integration_config.attributes or {}

        # Prefer full URI if provided; otherwise build from host/port/auth
        self.uri = attrs.get("uri")
        self.host = attrs.get("host")
        self.port = attrs.get("port")
        self.username = attrs.get("user") or attrs.get("username")
        self._password = attrs.get("password")
        self.database = attrs.get("database") or attrs.get("dbname")
        self.auth_source = attrs.get("auth_source")

        if not self.uri:
            auth = f"{self.username}:{self._password}@" if self.username and self._password else ""
            host = self.host or "localhost"
            port = self.port or 27017
            self.uri = f"mongodb://{auth}{host}:{port}"

    def execute_sql(self, sql: str) -> Optional[Any]:
        """Execute a MongoDB query. For parity, accepts a JSON-like command string.
        
        Notes:
            - This method expects 'sql' to be a JSON-like string with fields:
              {"collection": str, "operation": str, "query": dict, "options": dict}
            - Supported operations: find, insert_one, insert_many, update_one, update_many, delete_one, delete_many, aggregate
        """
        try:
            import json
            payload = json.loads(sql)
            collection_name = payload.get("collection")
            operation = payload.get("operation", "find")
            query = payload.get("query", {})
            options = payload.get("options", {})

            if not collection_name:
                raise ValueError("'collection' is required for MongoDB operations")

            client = MongoClient(self.uri)
            db = client[self.database]
            coll = db[collection_name]

            if operation == "find":
                cursor = coll.find(query, **options)
                return list(cursor)
            elif operation == "insert_one":
                return coll.insert_one(query).inserted_id
            elif operation == "insert_many":
                return coll.insert_many(query).inserted_ids
            elif operation == "update_one":
                update = options.get("update") or {}
                return coll.update_one(query, update).modified_count
            elif operation == "update_many":
                update = options.get("update") or {}
                return coll.update_many(query, update).modified_count
            elif operation == "delete_one":
                return coll.delete_one(query).deleted_count
            elif operation == "delete_many":
                return coll.delete_many(query).deleted_count
            elif operation == "aggregate":
                pipeline = payload.get("pipeline", [])
                return list(coll.aggregate(pipeline))
            else:
                raise ValueError(f"Unsupported MongoDB operation: {operation}")
        except Exception as e:
            print(f"MongoDB error: {e}")
            return None


