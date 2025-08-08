from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from ..enums import TaskType


@dataclass
class TaskInfo:
    """
    Information about a task type for project creation wizard.
    
    Contains task metadata including type, display name, description,
    and example image for UI presentation.
    """
    task_type: TaskType         # The task type enum
    name: str                   # Display name for UI
    description: str           # Detailed description of the task
    example_image: Optional[str] = None  # Path to example image (optional)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_type": self.task_type.value,
            "name": self.name,
            "description": self.description,
            "example_image": self.example_image
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskInfo":
        """Create TaskInfo from dictionary."""
        return cls(
            task_type=TaskType(data["task_type"]),
            name=data["name"],
            description=data["description"],
            example_image=data.get("example_image")
        )