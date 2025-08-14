"""
Serialization utilities for Autoppia SDK

This module provides safe JSON serialization and deserialization utilities.
"""

import json
from typing import Any, Dict, Optional, Callable
from .exceptions import SerializationError


def safe_json_dumps(
    obj: Any,
    indent: Optional[int] = None,
    ensure_ascii: bool = False,
    default: Optional[Callable] = None
) -> str:
    """
    Safely serialize an object to JSON string.
    
    Args:
        obj: Object to serialize
        indent: JSON indentation
        ensure_ascii: Whether to ensure ASCII output
        default: Custom serializer function
        
    Returns:
        JSON string
        
    Raises:
        SerializationError: If serialization fails
    """
    try:
        return json.dumps(
            obj,
            indent=indent,
            ensure_ascii=ensure_ascii,
            default=default or _default_serializer
        )
    except (TypeError, ValueError) as e:
        raise SerializationError(f"Failed to serialize object to JSON: {e}")


def safe_json_loads(
    json_str: str,
    encoding: Optional[str] = None
) -> Any:
    """
    Safely deserialize JSON string to object.
    
    Args:
        json_str: JSON string to deserialize
        encoding: String encoding
        
    Returns:
        Deserialized object
        
    Raises:
        SerializationError: If deserialization fails
    """
    try:
        if encoding:
            json_str = json_str.decode(encoding)
        return json.loads(json_str)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise SerializationError(f"Failed to deserialize JSON: {e}")


def _default_serializer(obj: Any) -> str:
    """Default serializer for non-serializable objects."""
    try:
        return str(obj)
    except Exception:
        return f"<non-serializable: {type(obj).__name__}>"


def safe_json_file_write(
    data: Any,
    file_path: str,
    indent: int = 2,
    ensure_ascii: bool = False
) -> None:
    """
    Safely write data to JSON file.
    
    Args:
        data: Data to write
        file_path: Target file path
        indent: JSON indentation
        ensure_ascii: Whether to ensure ASCII output
        
    Raises:
        SerializationError: If writing fails
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(
                data,
                f,
                indent=indent,
                ensure_ascii=ensure_ascii,
                default=_default_serializer
            )
    except (IOError, OSError) as e:
        raise SerializationError(f"Failed to write JSON file {file_path}: {e}")


def safe_json_file_read(file_path: str) -> Any:
    """
    Safely read data from JSON file.
    
    Args:
        file_path: Source file path
        
    Returns:
        Deserialized data
        
    Raises:
        SerializationError: If reading fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, OSError) as e:
        raise SerializationError(f"Failed to read JSON file {file_path}: {e}")
    except json.JSONDecodeError as e:
        raise SerializationError(f"Invalid JSON in file {file_path}: {e}")
