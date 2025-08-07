"""
Project configuration management for YOLOFlow projects.
"""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

try:
    import tomllib
except ImportError:
    import tomli as tomllib
import tomli_w


class TaskType(Enum):
    """Supported task types for YOLO projects."""
    CLASSIFICATION = "classification"
    DETECTION = "detection"
    SEGMENTATION = "segmentation"
    INSTANCE_SEGMENTATION = "instance_segmentation"
    KEYPOINT = "keypoint"
    ORIENTED_DETECTION = "oriented_detection"


class ProjectConfig:
    """
    Manages project configuration stored in yoloflow.toml.
    
    Handles project settings including datasets, models, training parameters,
    and custom user-defined fields.
    """
    
    def __init__(self, config_path: Union[str, Path]):
        """
        Initialize project configuration.
        
        Args:
            config_path: Path to the yoloflow.toml configuration file
        """
        self.config_path = Path(config_path)
        self._config_data = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from TOML file."""
        if self.config_path.exists():
            with open(self.config_path, 'rb') as f:
                self._config_data = tomllib.load(f)
        else:
            # Create default configuration
            self._config_data = self._create_default_config()
            self.save()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration structure."""
        return {
            "project": {
                "name": "",
                "task_type": TaskType.DETECTION.value,
                "created_at": datetime.now().isoformat(),
                "description": ""
            },
            "datasets": {
                "available": [],
                "current": ""
            },
            "models": {
                "available": [],
                "current": "",
                "pretrained": []
            },
            "training": {
                "history": [],
                "parameters": {
                    "epochs": 100,
                    "batch_size": 16,
                    "learning_rate": 0.01,
                    "image_size": 640
                }
            },
            "custom_fields": {}
        }
    
    def save(self):
        """Save current configuration to TOML file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'wb') as f:
            tomli_w.dump(self._config_data, f)
    
    # Project properties
    @property
    def project_name(self) -> str:
        return self._config_data.get("project", {}).get("name", "")
    
    @project_name.setter
    def project_name(self, value: str):
        if "project" not in self._config_data:
            self._config_data["project"] = {}
        self._config_data["project"]["name"] = value
    
    @property
    def task_type(self) -> TaskType:
        task_str = self._config_data.get("project", {}).get("task_type", TaskType.DETECTION.value)
        return TaskType(task_str)
    
    @task_type.setter
    def task_type(self, value: TaskType):
        if "project" not in self._config_data:
            self._config_data["project"] = {}
        self._config_data["project"]["task_type"] = value.value
    
    @property
    def description(self) -> str:
        return self._config_data.get("project", {}).get("description", "")
    
    @description.setter
    def description(self, value: str):
        if "project" not in self._config_data:
            self._config_data["project"] = {}
        self._config_data["project"]["description"] = value
    
    # Dataset management
    @property
    def available_datasets(self) -> List[str]:
        return self._config_data.get("datasets", {}).get("available", [])
    
    def add_dataset(self, dataset_name: str):
        """Add a dataset to the available list."""
        if "datasets" not in self._config_data:
            self._config_data["datasets"] = {"available": [], "current": None}
        if dataset_name not in self._config_data["datasets"]["available"]:
            self._config_data["datasets"]["available"].append(dataset_name)
    
    def remove_dataset(self, dataset_name: str):
        """Remove a dataset from the available list."""
        if "datasets" in self._config_data and dataset_name in self._config_data["datasets"]["available"]:
            self._config_data["datasets"]["available"].remove(dataset_name)
            if self._config_data["datasets"]["current"] == dataset_name:
                self._config_data["datasets"]["current"] = ""
    
    @property
    def current_dataset(self) -> Optional[str]:
        current = self._config_data.get("datasets", {}).get("current", "")
        return current if current else None
    
    @current_dataset.setter
    def current_dataset(self, dataset_name: Optional[str]):
        if "datasets" not in self._config_data:
            self._config_data["datasets"] = {"available": [], "current": ""}
        self._config_data["datasets"]["current"] = dataset_name or ""
    
    # Model management
    @property
    def available_models(self) -> List[str]:
        return self._config_data.get("models", {}).get("available", [])
    
    def add_model(self, model_name: str):
        """Add a model to the available list."""
        if "models" not in self._config_data:
            self._config_data["models"] = {"available": [], "current": "", "pretrained": []}
        if model_name not in self._config_data["models"]["available"]:
            self._config_data["models"]["available"].append(model_name)
    
    @property
    def current_model(self) -> Optional[str]:
        current = self._config_data.get("models", {}).get("current", "")
        return current if current else None
    
    @current_model.setter
    def current_model(self, model_name: Optional[str]):
        if "models" not in self._config_data:
            self._config_data["models"] = {"available": [], "current": "", "pretrained": []}
        self._config_data["models"]["current"] = model_name or ""
    
    # Training parameters
    @property
    def training_parameters(self) -> Dict[str, Any]:
        return self._config_data.get("training", {}).get("parameters", {})
    
    def set_training_parameter(self, key: str, value: Any):
        """Set a training parameter."""
        if "training" not in self._config_data:
            self._config_data["training"] = {"history": [], "parameters": {}}
        if "parameters" not in self._config_data["training"]:
            self._config_data["training"]["parameters"] = {}
        self._config_data["training"]["parameters"][key] = value
    
    def get_training_parameter(self, key: str, default: Any = None) -> Any:
        """Get a training parameter."""
        return self.training_parameters.get(key, default)
    
    # Training history
    def add_training_record(self, record: Dict[str, Any]):
        """Add a training history record."""
        if "training" not in self._config_data:
            self._config_data["training"] = {"history": [], "parameters": {}}
        if "history" not in self._config_data["training"]:
            self._config_data["training"]["history"] = []
        
        # Add timestamp if not present
        if "timestamp" not in record:
            record["timestamp"] = datetime.now().isoformat()
        
        self._config_data["training"]["history"].append(record)
    
    @property
    def training_history(self) -> List[Dict[str, Any]]:
        return self._config_data.get("training", {}).get("history", [])
    
    # Custom fields management
    def set_custom_field(self, key: str, value: str):
        """
        Set a custom field value.
        All custom fields are stored as strings for easy UI editing.
        """
        if "custom_fields" not in self._config_data:
            self._config_data["custom_fields"] = {}
        self._config_data["custom_fields"][key] = str(value)
    
    def get_custom_field(self, key: str, default: str = "") -> str:
        """Get a custom field value."""
        return self._config_data.get("custom_fields", {}).get(key, default)
    
    def remove_custom_field(self, key: str):
        """Remove a custom field."""
        if "custom_fields" in self._config_data and key in self._config_data["custom_fields"]:
            del self._config_data["custom_fields"][key]
    
    @property
    def custom_fields(self) -> Dict[str, str]:
        """Get all custom fields."""
        return self._config_data.get("custom_fields", {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the complete configuration as a dictionary."""
        return self._config_data.copy()
    
    def __repr__(self) -> str:
        return f"ProjectConfig('{self.config_path}', name='{self.project_name}', task='{self.task_type.value}')"
