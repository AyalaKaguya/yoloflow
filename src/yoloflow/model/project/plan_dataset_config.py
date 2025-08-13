"""
Dataset configuration for training plans.
"""

from dataclasses import dataclass
from typing import Dict, Any
from ..enums import DatasetTarget

@dataclass
class PlanDatasetConfig:
    """Configuration for a dataset in training plan."""
    name: str                # Dataset name
    target: DatasetTarget    # How to use this dataset
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "target": self.target.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanDatasetConfig":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            target=DatasetTarget(data["target"])
        )
