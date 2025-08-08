
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from .project_config import TaskType


@dataclass
class ModelInfo:
    """
    Information about a YOLO model.
    
    Contains model metadata including name, file, parameters, 
    supported tasks, and description.
    """
    name: str               # Display name of the model
    filename: str           # Model file name (e.g., "yolo11n.pt")
    parameters: str         # Parameter count (e.g., "2.6M", "25.3M")
    supported_tasks: Set[TaskType]  # Tasks this model supports
    description: str        # Model description
    
    def supports_task(self, task_type: TaskType) -> bool:
        """Check if model supports the given task type."""
        return task_type in self.supported_tasks
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "filename": self.filename,
            "parameters": self.parameters,
            "supported_tasks": [task.value for task in self.supported_tasks],
            "description": self.description
        }