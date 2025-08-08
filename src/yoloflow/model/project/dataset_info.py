from dataclasses import dataclass
from typing import Dict
from ..enums import DatasetType

@dataclass
class DatasetInfo:
    """Information about a dataset."""
    name: str
    path: str  # Relative path within project
    dataset_type: DatasetType
    description: str = ""
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for storage in config."""
        return {
            "name": self.name,
            "path": self.path,
            "type": self.dataset_type.value,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "DatasetInfo":
        """Create DatasetInfo from dictionary."""
        return cls(
            name=data["name"],
            path=data["path"],
            dataset_type=DatasetType(data["type"]),
            description=data.get("description", "")
        )