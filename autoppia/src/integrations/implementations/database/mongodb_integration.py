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
        self.user = attrs.get("user")
        self._password = attrs.get("password")
        self.dbname = attrs.get("dbname")
        self.auth_source = attrs.get("auth_source")

        if not self.uri:
            auth = f"{self.user}:{self._password}@" if self.user and self._password else ""
            host = self.host or "localhost"
            port = self.port or 27017
            self.uri = f"mongodb://{auth}{host}:{port}"

    def execute_sql(self, sql: str) -> Optional[Any]:
        """Execute a MongoDB query. Accepts a JSON command string.

        Payload shape:
            {
              "collection": str,                   # required
              "operation": str,                    # e.g., find, find_one, update_one, ...
              "query": dict,                       # filter or document depending on operation
              "options": dict,                     # operation-specific options
              "pipeline": list                     # for aggregate
            }

        Supported operations:
            - find, find_one
              options: projection, sort, limit, skip
            - insert_one, insert_many
            - update_one, update_many
              options: update (required), upsert (bool), array_filters (list)
            - replace_one
              options: replacement (required), upsert (bool)
            - delete_one, delete_many
            - find_one_and_update
              options: update (required), upsert (bool), return_document ("before"|"after"), array_filters (list)
            - distinct
              options: key (required)
            - count_documents
            - aggregate (uses top-level pipeline)
        """
        try:
            import json
            payload = json.loads(sql)
            client = MongoClient(self.uri)
            db = client[self.dbname]

            # Backward-compatible shape: {collection, operation, query, options, pipeline}
            if any(k in payload for k in ("collection", "operation")):
                collection_name = payload.get("collection")
                operation = payload.get("operation", "find")
                query = payload.get("query", {})
                options = payload.get("options", {})

                if not collection_name:
                    raise ValueError("'collection' is required for MongoDB operations")

                coll = db[collection_name]

            if operation == "find":
                projection = options.get("projection")
                sort = options.get("sort")
                limit = options.get("limit")
                skip = options.get("skip")

                cursor = coll.find(query, projection)
                if sort:
                    cursor = cursor.sort(sort)
                if skip:
                    cursor = cursor.skip(int(skip))
                if limit:
                    cursor = cursor.limit(int(limit))
                return list(cursor)
            elif operation == "find_one":
                projection = options.get("projection")
                return coll.find_one(query, projection)
            elif operation == "insert_one":
                return coll.insert_one(query).inserted_id
            elif operation == "insert_many":
                return coll.insert_many(query).inserted_ids
            elif operation == "update_one":
                update = options.get("update") or {}
                upsert = bool(options.get("upsert", False))
                array_filters = options.get("array_filters")
                kwargs = {"upsert": upsert}
                if array_filters:
                    kwargs["array_filters"] = array_filters
                return coll.update_one(query, update, **kwargs).modified_count
            elif operation == "update_many":
                update = options.get("update") or {}
                upsert = bool(options.get("upsert", False))
                array_filters = options.get("array_filters")
                kwargs = {"upsert": upsert}
                if array_filters:
                    kwargs["array_filters"] = array_filters
                return coll.update_many(query, update, **kwargs).modified_count
            elif operation == "replace_one":
                replacement = options.get("replacement") or {}
                upsert = bool(options.get("upsert", False))
                return coll.replace_one(query, replacement, upsert=upsert).modified_count
            elif operation == "delete_one":
                return coll.delete_one(query).deleted_count
            elif operation == "delete_many":
                return coll.delete_many(query).deleted_count
            elif operation == "find_one_and_update":
                update = options.get("update") or {}
                upsert = bool(options.get("upsert", False))
                return_after = options.get("return_document", "after")
                array_filters = options.get("array_filters")

                from pymongo import ReturnDocument
                rd = ReturnDocument.AFTER if str(return_after).lower() == "after" else ReturnDocument.BEFORE
                kwargs = {"upsert": upsert, "return_document": rd}
                if array_filters:
                    kwargs["array_filters"] = array_filters
                return coll.find_one_and_update(query, update, **kwargs)
            elif operation == "distinct":
                key = options.get("key")
                if not key:
                    raise ValueError("'options.key' is required for distinct operation")
                return coll.distinct(key, query)
            elif operation == "count_documents":
                return coll.count_documents(query)
            elif operation == "aggregate":
                pipeline = payload.get("pipeline", [])
                return list(coll.aggregate(pipeline))
            else:
                raise ValueError(f"Unsupported MongoDB operation: {operation}")

            # Command-style shape: { find: "col", filter: {...}, projection, sort, limit, skip }
            # Also supports: insertOne, insertMany, updateOne, updateMany, deleteOne, deleteMany,
            # replaceOne, findOne, findOneAndUpdate, distinct, countDocuments, aggregate
            else:
                # find
                if "find" in payload:
                    collection_name = payload.get("find")
                    coll = db[collection_name]
                    filter_doc = payload.get("filter", {})
                    projection = payload.get("projection")
                    sort = payload.get("sort")
                    limit = payload.get("limit")
                    skip = payload.get("skip")

                    cursor = coll.find(filter_doc, projection)
                    if sort:
                        if isinstance(sort, dict):
                            sort = list(sort.items())
                        cursor = cursor.sort(sort)
                    if skip:
                        cursor = cursor.skip(int(skip))
                    if limit:
                        cursor = cursor.limit(int(limit))
                    return list(cursor)

                # findOne
                if "findOne" in payload:
                    collection_name = payload.get("findOne")
                    coll = db[collection_name]
                    filter_doc = payload.get("filter", {})
                    projection = payload.get("projection")
                    return coll.find_one(filter_doc, projection)

                # insertOne
                if "insertOne" in payload:
                    collection_name = payload.get("insertOne")
                    coll = db[collection_name]
                    document = payload.get("document", {})
                    return coll.insert_one(document).inserted_id

                # insertMany
                if "insertMany" in payload:
                    collection_name = payload.get("insertMany")
                    coll = db[collection_name]
                    documents = payload.get("documents", [])
                    return coll.insert_many(documents).inserted_ids

                # updateOne
                if "updateOne" in payload:
                    collection_name = payload.get("updateOne")
                    coll = db[collection_name]
                    filter_doc = payload.get("filter", {})
                    update = payload.get("update") or {}
                    upsert = bool(payload.get("upsert", False))
                    array_filters = payload.get("arrayFilters")
                    kwargs = {"upsert": upsert}
                    if array_filters:
                        kwargs["array_filters"] = array_filters
                    return coll.update_one(filter_doc, update, **kwargs).modified_count

                # updateMany
                if "updateMany" in payload:
                    collection_name = payload.get("updateMany")
                    coll = db[collection_name]
                    filter_doc = payload.get("filter", {})
                    update = payload.get("update") or {}
                    upsert = bool(payload.get("upsert", False))
                    array_filters = payload.get("arrayFilters")
                    kwargs = {"upsert": upsert}
                    if array_filters:
                        kwargs["array_filters"] = array_filters
                    return coll.update_many(filter_doc, update, **kwargs).modified_count

                # replaceOne
                if "replaceOne" in payload:
                    collection_name = payload.get("replaceOne")
                    coll = db[collection_name]
                    filter_doc = payload.get("filter", {})
                    replacement = payload.get("replacement") or {}
                    upsert = bool(payload.get("upsert", False))
                    return coll.replace_one(filter_doc, replacement, upsert=upsert).modified_count

                # deleteOne
                if "deleteOne" in payload:
                    collection_name = payload.get("deleteOne")
                    coll = db[collection_name]
                    filter_doc = payload.get("filter", {})
                    return coll.delete_one(filter_doc).deleted_count

                # deleteMany
                if "deleteMany" in payload:
                    collection_name = payload.get("deleteMany")
                    coll = db[collection_name]
                    filter_doc = payload.get("filter", {})
                    return coll.delete_many(filter_doc).deleted_count

                # findOneAndUpdate
                if "findOneAndUpdate" in payload:
                    collection_name = payload.get("findOneAndUpdate")
                    coll = db[collection_name]
                    filter_doc = payload.get("filter", {})
                    update = payload.get("update") or {}
                    upsert = bool(payload.get("upsert", False))
                    return_after = payload.get("returnDocument", "after")
                    array_filters = payload.get("arrayFilters")
                    from pymongo import ReturnDocument
                    rd = ReturnDocument.AFTER if str(return_after).lower() == "after" else ReturnDocument.BEFORE
                    kwargs = {"upsert": upsert, "return_document": rd}
                    if array_filters:
                        kwargs["array_filters"] = array_filters
                    return coll.find_one_and_update(filter_doc, update, **kwargs)

                # distinct
                if "distinct" in payload:
                    collection_name = payload.get("distinct")
                    coll = db[collection_name]
                    key = payload.get("key")
                    if not key:
                        raise ValueError("'key' is required for distinct command")
                    filter_doc = payload.get("filter", {})
                    return coll.distinct(key, filter_doc)

                # countDocuments
                if "countDocuments" in payload:
                    collection_name = payload.get("countDocuments")
                    coll = db[collection_name]
                    filter_doc = payload.get("filter", {})
                    return coll.count_documents(filter_doc)

                # aggregate
                if "aggregate" in payload:
                    collection_name = payload.get("aggregate")
                    coll = db[collection_name]
                    pipeline = payload.get("pipeline", [])
                    return list(coll.aggregate(pipeline))

                raise ValueError("Unsupported MongoDB command payload")
        except Exception as e:
            print(f"MongoDB error: {e}")
            return None


