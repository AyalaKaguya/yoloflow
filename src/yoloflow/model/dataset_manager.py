"""
Dataset management for YOLOFlow projects.
"""

import os
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

from .project_config import ProjectConfig
from .dataset_info import DatasetInfo
from .dataset_type import DatasetType



class DatasetManager:
    """
    Manages datasets within a YOLOFlow project.
    
    Handles dataset information, importing from folders/zip files,
    and maintaining dataset records in the project configuration.
    """
    
    def __init__(self, project_config: ProjectConfig, project_path: Path):
        """
        Initialize dataset manager.
        
        Args:
            project_config: Project configuration instance
            project_path: Path to the project directory
        """
        self.config = project_config
        self.project_path = Path(project_path)
        self.dataset_dir = self.project_path / "dataset"
        
        # Ensure dataset directory exists
        self.dataset_dir.mkdir(exist_ok=True)
        
        # Load existing datasets from config
        self._load_datasets_from_config()
    
    def _load_datasets_from_config(self):
        """Load dataset information from project configuration."""
        # Check if new detailed dataset format exists
        detailed_datasets = self.config._config_data.get("datasets", {}).get("detailed", [])
        
        if not detailed_datasets:
            # Migrate from old simple format to new detailed format
            simple_datasets = self.config.available_datasets
            if simple_datasets:
                self._migrate_simple_datasets(simple_datasets)
        
        # Ensure detailed datasets section exists
        if "datasets" not in self.config._config_data:
            self.config._config_data["datasets"] = {"available": [], "current": "", "detailed": []}
        elif "detailed" not in self.config._config_data["datasets"]:
            self.config._config_data["datasets"]["detailed"] = []
    
    def _migrate_simple_datasets(self, simple_datasets: List[str]):
        """Migrate simple dataset names to detailed format."""
        detailed_datasets = []
        default_type = self.config.task_type
        
        for dataset_name in simple_datasets:
            dataset_info = DatasetInfo(
                name=dataset_name,
                path=f"dataset/{dataset_name}",
                dataset_type=DatasetType(default_type.value),
                description=""
            )
            detailed_datasets.append(dataset_info.to_dict())
        
        self.config._config_data["datasets"]["detailed"] = detailed_datasets
        self.config.save()
    
    @property
    def datasets(self) -> List[DatasetInfo]:
        """Get list of all datasets."""
        detailed_datasets = self.config._config_data.get("datasets", {}).get("detailed", [])
        return [DatasetInfo.from_dict(data) for data in detailed_datasets]
    
    def get_dataset(self, name: str) -> Optional[DatasetInfo]:
        """Get dataset by name."""
        for dataset in self.datasets:
            if dataset.name == name:
                return dataset
        return None
    
    def add_dataset(
        self,
        name: str,
        dataset_type: Optional[DatasetType] = None,
        description: str = ""
    ) -> DatasetInfo:
        """
        Add a new dataset entry.
        
        Args:
            name: Dataset name
            dataset_type: Dataset type (defaults to project task type)
            description: Dataset description
            
        Returns:
            DatasetInfo: Created dataset info
            
        Raises:
            ValueError: If dataset with same name already exists
        """
        # Check if dataset already exists
        if self.get_dataset(name):
            raise ValueError(f"Dataset '{name}' already exists")
        
        # Use project task type as default
        if dataset_type is None:
            dataset_type = DatasetType(self.config.task_type.value)
        
        # Create dataset info
        dataset_info = DatasetInfo(
            name=name,
            path=f"dataset/{name}",
            dataset_type=dataset_type,
            description=description
        )
        
        # Add to config
        detailed_datasets = self.config._config_data.get("datasets", {}).get("detailed", [])
        detailed_datasets.append(dataset_info.to_dict())
        self.config._config_data["datasets"]["detailed"] = detailed_datasets
        
        # Also add to simple available list for backward compatibility
        if name not in self.config.available_datasets:
            self.config.add_dataset(name)
        
        self.config.save()
        return dataset_info
    
    def remove_dataset(self, name: str, delete_files: bool = False):
        """
        Remove a dataset.
        
        Args:
            name: Dataset name to remove
            delete_files: Whether to delete dataset files from disk
            
        Raises:
            ValueError: If dataset doesn't exist
        """
        dataset = self.get_dataset(name)
        if not dataset:
            raise ValueError(f"Dataset '{name}' not found")
        
        # Remove from detailed list
        detailed_datasets = self.config._config_data.get("datasets", {}).get("detailed", [])
        detailed_datasets = [d for d in detailed_datasets if d["name"] != name]
        self.config._config_data["datasets"]["detailed"] = detailed_datasets
        
        # Remove from simple list
        self.config.remove_dataset(name)
        
        # Delete files if requested
        if delete_files:
            dataset_path = self.project_path / dataset.path
            if dataset_path.exists():
                shutil.rmtree(dataset_path)
        
        self.config.save()
    
    def update_dataset(
        self,
        name: str,
        new_name: Optional[str] = None,
        dataset_type: Optional[DatasetType] = None,
        description: Optional[str] = None
    ):
        """
        Update dataset information.
        
        Args:
            name: Current dataset name
            new_name: New dataset name (optional)
            dataset_type: New dataset type (optional)
            description: New description (optional)
            
        Raises:
            ValueError: If dataset doesn't exist or new name conflicts
        """
        dataset = self.get_dataset(name)
        if not dataset:
            raise ValueError(f"Dataset '{name}' not found")
        
        # Check for name conflicts
        if new_name and new_name != name and self.get_dataset(new_name):
            raise ValueError(f"Dataset '{new_name}' already exists")
        
        # Update dataset info
        if new_name:
            dataset.name = new_name
        if dataset_type:
            dataset.dataset_type = dataset_type
        if description is not None:
            dataset.description = description
        
        # Update in config
        detailed_datasets = self.config._config_data.get("datasets", {}).get("detailed", [])
        for i, d in enumerate(detailed_datasets):
            if d["name"] == name:
                detailed_datasets[i] = dataset.to_dict()
                break
        
        # Update simple list if name changed
        if new_name and new_name != name:
            self.config.remove_dataset(name)
            self.config.add_dataset(new_name)
        
        self.config.save()
    
    def import_from_folder(
        self,
        source_path: Union[str, Path],
        dataset_name: str,
        dataset_type: Optional[DatasetType] = None,
        description: str = ""
    ) -> DatasetInfo:
        """
        Import dataset from a folder.
        
        Args:
            source_path: Path to source folder
            dataset_name: Name for the dataset
            dataset_type: Dataset type (defaults to project task type)
            description: Dataset description
            
        Returns:
            DatasetInfo: Created dataset info
            
        Raises:
            FileNotFoundError: If source folder doesn't exist
            ValueError: If dataset name already exists
        """
        source_path = Path(source_path)
        if not source_path.exists() or not source_path.is_dir():
            raise FileNotFoundError(f"Source folder does not exist: {source_path}")
        
        # Create dataset entry
        dataset_info = self.add_dataset(dataset_name, dataset_type, description)
        
        # Copy folder to dataset directory
        target_path = self.project_path / dataset_info.path
        try:
            if target_path.exists():
                shutil.rmtree(target_path)
            shutil.copytree(source_path, target_path)
        except Exception as e:
            # Rollback dataset creation if copy fails
            self.remove_dataset(dataset_name, delete_files=False)
            raise RuntimeError(f"Failed to copy dataset folder: {e}")
        
        return dataset_info
    
    def import_from_zip(
        self,
        zip_path: Union[str, Path],
        dataset_name: str,
        dataset_type: Optional[DatasetType] = None,
        description: str = ""
    ) -> DatasetInfo:
        """
        Import dataset from a ZIP file.
        
        Args:
            zip_path: Path to ZIP file
            dataset_name: Name for the dataset
            dataset_type: Dataset type (defaults to project task type)
            description: Dataset description
            
        Returns:
            DatasetInfo: Created dataset info
            
        Raises:
            FileNotFoundError: If ZIP file doesn't exist
            ValueError: If dataset name already exists or ZIP is invalid
        """
        zip_path = Path(zip_path)
        if not zip_path.exists() or not zip_path.is_file():
            raise FileNotFoundError(f"ZIP file does not exist: {zip_path}")
        
        # Create dataset entry
        dataset_info = self.add_dataset(dataset_name, dataset_type, description)
        
        # Extract ZIP to dataset directory
        target_path = self.project_path / dataset_info.path
        try:
            target_path.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_path)
                
        except Exception as e:
            # Rollback dataset creation if extraction fails
            self.remove_dataset(dataset_name, delete_files=True)
            raise RuntimeError(f"Failed to extract ZIP file: {e}")
        
        return dataset_info
    
    def import_dataset(
        self,
        source_path: Union[str, Path],
        dataset_name: str,
        dataset_type: Optional[DatasetType] = None,
        description: str = ""
    ) -> DatasetInfo:
        """
        Auto-detect import method based on source path.
        
        Args:
            source_path: Path to source (folder or ZIP file)
            dataset_name: Name for the dataset
            dataset_type: Dataset type (defaults to project task type)
            description: Dataset description
            
        Returns:
            DatasetInfo: Created dataset info
        """
        source_path = Path(source_path)
        
        if source_path.is_dir():
            return self.import_from_folder(source_path, dataset_name, dataset_type, description)
        elif source_path.is_file() and source_path.suffix.lower() == '.zip':
            return self.import_from_zip(source_path, dataset_name, dataset_type, description)
        else:
            raise ValueError(f"Unsupported source type: {source_path}")
    
    def get_dataset_path(self, name: str) -> Optional[Path]:
        """Get absolute path to dataset directory."""
        dataset = self.get_dataset(name)
        if dataset:
            return self.project_path / dataset.path
        return None
    
    def list_dataset_files(self, name: str) -> List[Path]:
        """List all files in a dataset directory."""
        dataset_path = self.get_dataset_path(name)
        if not dataset_path or not dataset_path.exists():
            return []
        
        files = []
        for root, dirs, filenames in os.walk(dataset_path):
            for filename in filenames:
                files.append(Path(root) / filename)
        
        return files
    
    @property
    def current_dataset(self) -> Optional[DatasetInfo]:
        """Get current active dataset."""
        current_name = self.config.current_dataset
        if current_name:
            return self.get_dataset(current_name)
        return None
    
    @current_dataset.setter
    def current_dataset(self, dataset_name: Optional[str]):
        """Set current active dataset."""
        if dataset_name and not self.get_dataset(dataset_name):
            raise ValueError(f"Dataset '{dataset_name}' not found")
        self.config.current_dataset = dataset_name
        self.config.save()
