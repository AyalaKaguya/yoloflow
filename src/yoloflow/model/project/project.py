"""
Project management for YOLOFlow projects.
"""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, List, Dict, Any

from .project_config import ProjectConfig, TaskType
from .dataset_manager import DatasetManager
from .project_model_manager import ProjectModelManager
from .project_plan_manager import ProjectPlanManager


class Project:
    """
    Represents a YOLOFlow project with its directory structure and configuration.
    
    A project consists of:
    - yoloflow.toml: Project configuration
    - dataset/: Directory for datasets
    - model/: Directory for trained models
    - pretrain/: Directory for pretrained weights
    - runs/: Directory for training logs and results
    """
    
    REQUIRED_DIRS = ["dataset", "model", "pretrain", "runs", "plan"]
    CONFIG_FILE = "yoloflow.toml"
    
    def __init__(self, project_path: Union[str, Path]):
        """
        Initialize a project from an existing directory.
        
        Args:
            project_path: Path to the project directory
            
        Raises:
            FileNotFoundError: If project directory doesn't exist
            ValueError: If directory is not a valid YOLOFlow project
        """
        self.project_path = Path(project_path).resolve()
        
        if not self.project_path.exists():
            raise FileNotFoundError(f"Project directory does not exist: {self.project_path}")
        
        if not self.project_path.is_dir():
            raise ValueError(f"Project path is not a directory: {self.project_path}")
        
        # Load or create configuration
        config_path = self.project_path / self.CONFIG_FILE
        self.config = ProjectConfig(config_path)
        
        # Initialize dataset manager
        self.dataset_manager = DatasetManager(self.project_path, self.config)
        
        # Initialize model manager
        self.model_manager = ProjectModelManager(self.project_path, self.config)
        
        # Initialize plan manager
        self.plan_manager = ProjectPlanManager(self.project_path, self.config)
        
        # Validate project structure
        self._ensure_project_structure()
    
    @classmethod
    def create_new(
        cls,
        project_path: Union[str, Path],
        project_name: str,
        task_type: TaskType,
        description: str = ""
    ) -> "Project":
        """
        Create a new YOLOFlow project.
        
        Args:
            project_path: Path where to create the project directory
            project_name: Name of the project
            task_type: Type of the project (detection, classification, etc.)
            description: Optional project description
            
        Returns:
            Project: New project instance
            
        Raises:
            FileExistsError: If project directory already exists
        """
        project_path = Path(project_path).resolve()
        
        if project_path.exists():
            raise FileExistsError(f"Project directory already exists: {project_path}")
        
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create project structure
        for dir_name in cls.REQUIRED_DIRS:
            (project_path / dir_name).mkdir(exist_ok=True)
        
        # Create and configure project
        project = cls(project_path)
        project.config.project_name = project_name
        project.config.task_type = task_type
        project.config.description = description
        project.config.save()
        
        return project
    
    def _ensure_project_structure(self):
        """Ensure all required directories exist."""
        for dir_name in self.REQUIRED_DIRS:
            dir_path = self.project_path / dir_name
            dir_path.mkdir(exist_ok=True)
    
    @property
    def name(self) -> str:
        """Get project name."""
        return self.config.project_name or self.project_path.name
    
    @property
    def task_type(self) -> TaskType:
        """Get project task type."""
        return self.config.task_type
    
    @property
    def description(self) -> str:
        """Get project description."""
        return self.config.description
    
    @property
    def dataset_dir(self) -> Path:
        """Get dataset directory path."""
        return self.project_path / "dataset"
    
    @property
    def model_dir(self) -> Path:
        """Get model directory path."""
        return self.project_path / "model"
    
    @property
    def pretrain_dir(self) -> Path:
        """Get pretrained weights directory path."""
        return self.project_path / "pretrain"
    
    @property
    def runs_dir(self) -> Path:
        """Get training runs directory path."""
        return self.project_path / "runs"
    
    @property
    def plan_dir(self) -> Path:
        """Get training plans directory path."""
        return self.project_path / "plan"
        return self.project_path / "runs"
    
    @property
    def config_file(self) -> Path:
        """Get configuration file path."""
        return self.project_path / self.CONFIG_FILE
    
    def is_valid(self) -> bool:
        """
        Check if the project directory structure is valid.
        
        Returns:
            bool: True if project is valid
        """
        try:
            # Check if all required directories exist
            for dir_name in self.REQUIRED_DIRS:
                if not (self.project_path / dir_name).exists():
                    return False
            
            # Check if config file exists
            if not self.config_file.exists():
                return False
            
            return True
        except Exception:
            return False
    
    def get_datasets(self) -> List[str]:
        """
        Get list of available datasets in the project.
        
        Returns:
            list: List of dataset names
        """
        datasets = []
        if self.dataset_dir.exists():
            for item in self.dataset_dir.iterdir():
                if item.is_dir():
                    datasets.append(item.name)
        return sorted(datasets)
    
    def get_models(self) -> List[str]:
        """
        Get list of available trained models in the project.
        
        Returns:
            list: List of model file names (compatibility method)
        """
        return self.model_manager.get_trained_model_filenames()
    
    def get_pretrained_models(self) -> List[str]:
        """
        Get list of available pretrained models in the project.
        
        Returns:
            list: List of pretrained model file names (compatibility method)
        """
        return self.model_manager.get_pretrained_model_filenames()
    
    def get_model_info_list(self) -> List:
        """
        Get list of all model information objects.
        
        Returns:
            list: List of ProjectModelInfo objects for all models
        """
        result = []
        result.extend(self.model_manager.get_pretrained_models())
        result.extend(self.model_manager.get_trained_models())
        return result
    
    def get_pretrained_model_info_list(self) -> List:
        """
        Get list of pretrained model information objects.
        
        Returns:
            list: List of ProjectModelInfo objects for pretrained models
        """
        return self.model_manager.get_pretrained_models()
    
    def get_trained_model_info_list(self) -> List:
        """
        Get list of trained model information objects.
        
        Returns:
            list: List of ProjectModelInfo objects for trained models
        """
        return self.model_manager.get_trained_models()
    
    def get_training_runs(self) -> List[str]:
        """
        Get list of training run directories.
        
        Returns:
            list: List of training run names
        """
        runs = []
        if self.runs_dir.exists():
            for item in self.runs_dir.iterdir():
                if item.is_dir():
                    runs.append(item.name)
        return sorted(runs, reverse=True)  # Most recent first
    
    def save_config(self):
        """Save project configuration."""
        self.config.save()
    
    def get_project_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive project summary including all managers.
        
        Returns:
            Dictionary with project statistics
        """
        model_summary = self.model_manager.get_model_summary()
        return {
            "name": self.name,
            "task_type": self.task_type.value,
            "datasets": len(self.get_datasets()),
            "pretrained_models": model_summary["pretrained_models"],
            "trained_models": model_summary["trained_models"],
            "training_plans": self.plan_manager.get_plan_count(),
            "completed_plans": len(self.plan_manager.get_plans_by_status(True)),
            "pending_plans": len(self.plan_manager.get_plans_by_status(False)),
            "training_runs": len(self.get_training_runs())
        }
    
    def delete(self, confirm: bool = False):
        """
        Delete the entire project directory.
        
        Args:
            confirm: If True, proceed with deletion. Safety measure to prevent accidental deletion.
            
        Raises:
            ValueError: If confirm is False
        """
        if not confirm:
            raise ValueError("Must confirm project deletion by setting confirm=True")
        
        if self.project_path.exists():
            shutil.rmtree(self.project_path)
    
    def __str__(self) -> str:
        return f"Project('{self.name}', {self.task_type.value}, {self.project_path})"
    
    def __repr__(self) -> str:
        return self.__str__()
