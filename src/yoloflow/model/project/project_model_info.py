"""
Project model information management.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..enums import TaskType


@dataclass
class ProjectModelInfo:
    """
    Information about a model in a project.
    
    Stores metadata about both pretrained and trained models.
    """
    
    name: str  # Display name for the model
    filename: str  # Actual filename (e.g., "yolo11n.pt")
    description: str  # Model description
    parameters: int  # Number of parameters (e.g., 2000000 for 2M)
    task_type: TaskType  # Task type this model supports
    source: str  # Source of the model ("project_creation", "plan_created", "imported")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "filename": self.filename,
            "description": self.description,
            "parameters": self.parameters,
            "task_type": self.task_type.value,
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectModelInfo":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            filename=data["filename"],
            description=data.get("description", ""),
            parameters=data.get("parameters", 0),
            task_type=TaskType(data.get("task_type", TaskType.DETECTION.value)),
            source=data.get("source", "imported")
        )
    
    @classmethod
    def create_pretrained(
        cls,
        filename: str,
        name: Optional[str] = None,
        description: str = "",
        parameters: int = 0,
        task_type: TaskType = TaskType.DETECTION
    ) -> "ProjectModelInfo":
        """Create info for a pretrained model."""
        if name is None:
            # Extract name from filename (remove .pt extension)
            name = filename.replace('.pt', '').replace('_', ' ').title()
        
        return cls(
            name=name,
            filename=filename,
            description=description,
            parameters=parameters,
            task_type=task_type,
            source="imported"
        )
    
    @classmethod
    def create_trained(
        cls,
        filename: str,
        plan_name: str,
        description: str = "",
        parameters: int = 0,
        task_type: TaskType = TaskType.DETECTION
    ) -> "ProjectModelInfo":
        """Create info for a trained model."""
        return cls(
            name=f"{plan_name} - Trained Model",
            filename=filename,
            description=description or f"Model trained from plan: {plan_name}",
            parameters=parameters,
            task_type=task_type,
            source="plan_created"
        )
    
    def __str__(self) -> str:
        return f"{self.name} ({self.filename})"
    
    def __repr__(self) -> str:
        return f"ProjectModelInfo(name='{self.name}', filename='{self.filename}', source='{self.source}')"
