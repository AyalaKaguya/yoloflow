"""
Training results for training plans.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class TrainingResults:
    """Training result models."""
    best_model: Optional[str] = None    # Path to best model
    latest_model: Optional[str] = None  # Path to latest model
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {}
        if self.best_model is not None:
            result["best_model"] = self.best_model
        if self.latest_model is not None:
            result["latest_model"] = self.latest_model
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainingResults":
        """Create from dictionary."""
        return cls(
            best_model=data.get("best_model"),
            latest_model=data.get("latest_model")
        )
