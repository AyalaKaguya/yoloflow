"""
Project configuration management for YOLOFlow projects.
"""

import json
from datetime import datetime
from ..enums import TaskType
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

try:
    import tomllib
except ImportError:
    import tomli as tomllib
import tomli_w

from .project_model_info import ProjectModelInfo
from .plan_info import PlanInfo


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
                "detailed": []
            },
            "models": {
                "available": [],
                "detailed": []
            },
            "plans": {
                "available": [],
                "detailed": []
            },
            "training": {
                "history": []
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
            # Only check current if it exists in the new structure
            if "current" in self._config_data["datasets"] and self._config_data["datasets"]["current"] == dataset_name:
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
        """Get list of available model names for quick access."""
        return self._config_data.get("models", {}).get("available", [])
    
    @property
    def model_details(self) -> List[ProjectModelInfo]:
        """Get detailed model information."""
        detailed = self._config_data.get("models", {}).get("detailed", [])
        return [ProjectModelInfo.from_dict(model_data) for model_data in detailed]
    
    def add_model(self, model_info: ProjectModelInfo):
        """Add a model with detailed information."""
        if "models" not in self._config_data:
            self._config_data["models"] = {"available": [], "detailed": []}
        
        # Add to available list if not present
        if model_info.filename not in self._config_data["models"]["available"]:
            self._config_data["models"]["available"].append(model_info.filename)
        
        # Add to detailed list (remove existing if updating)
        detailed = self._config_data["models"]["detailed"]
        detailed = [m for m in detailed if m["filename"] != model_info.filename]
        detailed.append(model_info.to_dict())
        self._config_data["models"]["detailed"] = detailed
    
    def remove_model(self, filename: str):
        """Remove a model by filename."""
        if "models" in self._config_data:
            # Remove from available list
            if filename in self._config_data["models"]["available"]:
                self._config_data["models"]["available"].remove(filename)
            
            # Remove from detailed list
            detailed = self._config_data["models"]["detailed"]
            detailed = [m for m in detailed if m["filename"] != filename]
            self._config_data["models"]["detailed"] = detailed
    
    def get_model_info(self, filename: str) -> Optional[ProjectModelInfo]:
        """Get detailed model information by filename."""
        for model_info in self.model_details:
            if model_info.filename == filename:
                return model_info
        return None
    
    def has_model(self, filename: str) -> bool:
        """Check if a model exists in the configuration."""
        return filename in self.available_models
    
    # Legacy pretrained model support (for backwards compatibility)
    @property
    def pretrained_models(self) -> List[str]:
        """Get list of pretrained model filenames (legacy support)."""
        pretrained = []
        for model_info in self.model_details:
            if model_info.source in ["imported", "project_creation"]:
                pretrained.append(model_info.filename)
        return pretrained
    
    def add_pretrained_model(self, model_name: str):
        """Add a pretrained model (legacy support)."""
        # Check if already exists in detailed models
        if not self.has_model(model_name):
            model_info = ProjectModelInfo.create_pretrained(
                filename=model_name,
                task_type=self.task_type
            )
            self.add_model(model_info)
    
    def remove_pretrained_model(self, model_name: str):
        """Remove a pretrained model (legacy support)."""
        self.remove_model(model_name)
    
    def has_pretrained_model(self, model_name: str) -> bool:
        """Check if a pretrained model exists (legacy support)."""
        return model_name in self.pretrained_models
    
    # Plan management
    @property
    def available_plans(self) -> List[str]:
        """Get list of available plan IDs for quick access."""
        return self._config_data.get("plans", {}).get("available", [])
    
    @property
    def plan_details(self) -> List[PlanInfo]:
        """Get detailed plan information."""
        detailed = self._config_data.get("plans", {}).get("detailed", [])
        return [PlanInfo.from_dict(plan_data) for plan_data in detailed]
    
    def add_plan(self, plan_info: PlanInfo):
        """Add a plan with detailed information."""
        if "plans" not in self._config_data:
            self._config_data["plans"] = {"available": [], "detailed": []}
        
        # Add to available list if not present
        if plan_info.plan_id not in self._config_data["plans"]["available"]:
            self._config_data["plans"]["available"].append(plan_info.plan_id)
        
        # Add to detailed list (remove existing if updating)
        detailed = self._config_data["plans"]["detailed"]
        detailed = [p for p in detailed if p["plan_id"] != plan_info.plan_id]
        detailed.append(plan_info.to_dict())
        self._config_data["plans"]["detailed"] = detailed
    
    def remove_plan(self, plan_id: str):
        """Remove a plan by ID."""
        if "plans" in self._config_data:
            # Remove from available list
            if plan_id in self._config_data["plans"]["available"]:
                self._config_data["plans"]["available"].remove(plan_id)
            
            # Remove from detailed list
            detailed = self._config_data["plans"]["detailed"]
            detailed = [p for p in detailed if p["plan_id"] != plan_id]
            self._config_data["plans"]["detailed"] = detailed
    
    def get_plan_info(self, plan_id: str) -> Optional[PlanInfo]:
        """Get detailed plan information by ID."""
        for plan_info in self.plan_details:
            if plan_info.plan_id == plan_id:
                return plan_info
        return None
    
    def update_plan_status(self, plan_id: str, status: str):
        """Update plan status."""
        plan_info = self.get_plan_info(plan_id)
        if plan_info:
            plan_info.update_status(status)
            self.add_plan(plan_info)  # Update in config
    
    def has_plan(self, plan_id: str) -> bool:
        """Check if a plan exists in the configuration."""
        return plan_id in self.available_plans
    
    # Training history
    def add_training_record(self, record: Dict[str, Any]):
        """Add a training history record."""
        if "training" not in self._config_data:
            self._config_data["training"] = {"history": []}
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
