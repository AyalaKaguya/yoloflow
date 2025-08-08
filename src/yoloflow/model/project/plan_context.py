"""
Training plan context information.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib
import tomli_w

from ..enums import TaskType
from .dataset_config import DatasetConfig, DatasetTarget
from .training_parameters import TrainingParameters
from .validation_parameters import ValidationParameters
from .training_results import TrainingResults


class PlanContext:
    """
    Training plan context information.
    
    Contains all information about a training plan including parameters,
    datasets, models, and results.
    """
    
    def __init__(
        self,
        plan_id: str,
        name: str,
        project_path: Path,
        task_type: TaskType,
        pretrained_model: Optional[str] = None
    ):
        """
        Initialize plan context.
        
        Args:
            plan_id: Unique plan identifier (UUID)
            name: User-defined plan name
            project_path: Path to the project directory
            task_type: Project task type
            pretrained_model: Path to pretrained model (relative to project)
        """
        self.plan_id = plan_id
        self.name = name
        self.project_path = Path(project_path)
        self.task_type = task_type
        self.pretrained_model = pretrained_model
        
        # Default parameters
        self.training_params = TrainingParameters()
        self.validation_params = ValidationParameters()
        self.datasets: List[DatasetConfig] = []
        self.results = TrainingResults()
        
        # Metadata
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        
        # Plan file path
        self.plan_file = self.project_path / "model" / f"{self.plan_id}.toml"
    
    @classmethod
    def create_new(
        cls,
        name: str,
        project_path: Path,
        task_type: TaskType,
        pretrained_model: Optional[str] = None
    ) -> "PlanContext":
        """
        Create a new training plan with generated UUID.
        
        Args:
            name: User-defined plan name
            project_path: Path to the project directory
            task_type: Project task type
            pretrained_model: Path to pretrained model
            
        Returns:
            New PlanContext instance
        """
        plan_id = str(uuid.uuid4())
        return cls(plan_id, name, project_path, task_type, pretrained_model)
    
    @classmethod
    def load_from_file(cls, plan_file: Path) -> "PlanContext":
        """
        Load plan context from TOML file.
        
        Args:
            plan_file: Path to plan TOML file
            
        Returns:
            Loaded PlanContext instance
            
        Raises:
            FileNotFoundError: If plan file doesn't exist
            ValueError: If plan file is invalid
        """
        if not plan_file.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_file}")
        
        try:
            with open(plan_file, 'rb') as f:
                data = tomllib.load(f)
            
            # Extract plan ID from filename
            plan_id = plan_file.stem
            
            # Create plan context
            plan = cls(
                plan_id=plan_id,
                name=data["plan"]["name"],
                project_path=plan_file.parent.parent,  # Go up from model/ to project/
                task_type=TaskType(data["plan"]["task_type"]),
                pretrained_model=data["plan"].get("pretrained_model")
            )
            
            # Load parameters
            if "training" in data:
                plan.training_params = TrainingParameters.from_dict(data["training"])
            
            if "validation" in data:
                plan.validation_params = ValidationParameters.from_dict(data["validation"])
            
            # Load datasets
            if "datasets" in data:
                plan.datasets = [DatasetConfig.from_dict(d) for d in data["datasets"]]
            
            # Load results
            if "results" in data:
                plan.results = TrainingResults.from_dict(data["results"])
            
            # Load metadata
            plan.created_at = data["plan"].get("created_at", datetime.now().isoformat())
            plan.updated_at = data["plan"].get("updated_at", datetime.now().isoformat())
            
            return plan
            
        except Exception as e:
            raise ValueError(f"Invalid plan file format: {e}")
    
    def save(self):
        """Save plan context to TOML file."""
        # Ensure model directory exists
        self.plan_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Update timestamp
        self.updated_at = datetime.now().isoformat()
        
        # Prepare data for serialization
        data = {
            "plan": {
                "name": self.name,
                "task_type": self.task_type.value,
                "created_at": self.created_at,
                "updated_at": self.updated_at
            },
            "training": self.training_params.to_dict(),
            "validation": self.validation_params.to_dict(),
            "datasets": [d.to_dict() for d in self.datasets],
            "results": self.results.to_dict()
        }
        
        # Add pretrained_model only if it's not None
        if self.pretrained_model is not None:
            data["plan"]["pretrained_model"] = self.pretrained_model
        
        # Save to file
        with open(self.plan_file, 'wb') as f:
            tomli_w.dump(data, f)
    
    def add_dataset(self, dataset_name: str, target: DatasetTarget):
        """Add a dataset to the training plan."""
        dataset_config = DatasetConfig(name=dataset_name, target=target)
        
        # Remove existing dataset with same name
        self.datasets = [d for d in self.datasets if d.name != dataset_name]
        
        # Add new dataset
        self.datasets.append(dataset_config)
    
    def remove_dataset(self, dataset_name: str):
        """Remove a dataset from the training plan."""
        self.datasets = [d for d in self.datasets if d.name != dataset_name]
    
    def update_training_params(self, **kwargs):
        """Update training parameters."""
        for key, value in kwargs.items():
            if hasattr(self.training_params, key):
                setattr(self.training_params, key, value)
            else:
                # Add to extra_params
                self.training_params.extra_params[key] = value
    
    def update_validation_params(self, **kwargs):
        """Update validation parameters."""
        for key, value in kwargs.items():
            if hasattr(self.validation_params, key):
                setattr(self.validation_params, key, value)
    
    def set_results(self, best_model: Optional[str] = None, latest_model: Optional[str] = None):
        """Set training result models."""
        if best_model is not None:
            self.results.best_model = best_model
        if latest_model is not None:
            self.results.latest_model = latest_model
    
    def get_dataset_configs(self) -> List[DatasetConfig]:
        """Get all dataset configurations."""
        return self.datasets.copy()
    
    def get_dataset_by_target(self, target: DatasetTarget) -> List[DatasetConfig]:
        """Get datasets by target type."""
        return [d for d in self.datasets if d.target == target]
    
    def has_results(self) -> bool:
        """Check if plan has training results."""
        return self.results.best_model is not None or self.results.latest_model is not None
    
    def delete(self):
        """Delete the plan file."""
        if self.plan_file.exists():
            self.plan_file.unlink()
    
    def __str__(self) -> str:
        return f"PlanContext('{self.name}', id={self.plan_id[:8]}...)"
    
    def __repr__(self) -> str:
        return self.__str__()
