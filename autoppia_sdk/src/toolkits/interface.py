from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class UserToolkit(BaseModel):
    """A model representing a user's toolkit configuration for code analysis and processing.

    This class defines the structure for toolkit configurations, including the toolkit's name,
    context data, instructions, and associated files.

    Attributes:
        toolkit_name (str): The name identifier of the toolkit.
        context (Dict[str, Any], optional): Additional contextual data for the toolkit.
            Defaults to None.
        instruction (str, optional): Specific instructions for toolkit execution.
            Defaults to None.
        context_files (List[str], optional): List of file paths relevant to the toolkit's context.
            Defaults to None.
    """
    toolkit_name: str
    context: Dict[str, Any] = None
    instruction: Optional[str] = None
    context_files: Optional[List[str]] = None
