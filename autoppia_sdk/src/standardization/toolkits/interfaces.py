from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class UserToolkit(BaseModel):
    toolkit_name: str
    context: Dict[str, Any] = None
    instruction: Optional[str] = None
    context_files: Optional[List[str]] = None
