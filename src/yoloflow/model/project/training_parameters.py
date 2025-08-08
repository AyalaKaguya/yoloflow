"""
Training parameters for training plans.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class TrainingParameters:
    """Core training parameters."""
    epochs: int = 100           # Training epochs
    learning_rate: float = 0.01 # Learning rate
    input_size: int = 640       # Input image size
    batch_size: int = 16        # Batch size
    extra_params: Dict[str, Any] = field(default_factory=dict)  # Additional parameters
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "epochs": self.epochs,
            "learning_rate": self.learning_rate,
            "input_size": self.input_size,
            "batch_size": self.batch_size,
            "extra_params": self.extra_params
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainingParameters":
        """Create from dictionary."""
        return cls(
            epochs=data.get("epochs", 100),
            learning_rate=data.get("learning_rate", 0.01),
            input_size=data.get("input_size", 640),
            batch_size=data.get("batch_size", 16),
            extra_params=data.get("extra_params", {})
        )
