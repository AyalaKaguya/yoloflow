"""
Test project management functionality.
"""

import tempfile
import pytest
import gc
import time
from pathlib import Path
from yoloflow.model import Project, ProjectConfig, TaskType
from yoloflow.service import ProjectManager


class TestProjectConfig:
    """Test ProjectConfig class."""
    
    def test_create_default_config(self):
        """Test creating a default configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test.toml"
            config = ProjectConfig(config_path)
            
            # Test default values
            assert config.project_name == ""
            assert config.task_type == TaskType.DETECTION
            assert len(config.available_datasets) == 0
            assert config.current_dataset is None
            
            # Test file was created
            assert config_path.exists()
    
    def test_project_properties(self):
        """Test project property setters and getters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test.toml"
            config = ProjectConfig(config_path)
            
            # Set properties
            config.project_name = "Test Project"
            config.task_type = TaskType.CLASSIFICATION
            config.description = "Test description"
            
            # Test properties
            assert config.project_name == "Test Project"
            assert config.task_type == TaskType.CLASSIFICATION
            assert config.description == "Test description"
            
            # Save and reload
            config.save()
            config2 = ProjectConfig(config_path)
            assert config2.project_name == "Test Project"
            assert config2.task_type == TaskType.CLASSIFICATION
    
    def test_dataset_management(self):
        """Test dataset management functions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test.toml"
            config = ProjectConfig(config_path)
            
            # Add datasets
            config.add_dataset("dataset1")
            config.add_dataset("dataset2")
            
            assert "dataset1" in config.available_datasets
            assert "dataset2" in config.available_datasets
            assert len(config.available_datasets) == 2
            
            # Set current dataset
            config.current_dataset = "dataset1"
            assert config.current_dataset == "dataset1"
            
            # Remove dataset
            config.remove_dataset("dataset1")
            assert "dataset1" not in config.available_datasets
            assert config.current_dataset is None  # Should be cleared
    
    def test_custom_fields(self):
        """Test custom fields management."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test.toml"
            config = ProjectConfig(config_path)
            
            # Set custom fields
            config.set_custom_field("my_field", "my_value")
            config.set_custom_field("another_field", 123)  # Should be converted to string
            
            assert config.get_custom_field("my_field") == "my_value"
            assert config.get_custom_field("another_field") == "123"
            assert config.get_custom_field("nonexistent", "default") == "default"
            
            # Check all custom fields
            fields = config.custom_fields
            assert "my_field" in fields
            assert "another_field" in fields
            
            # Remove field
            config.remove_custom_field("my_field")
            assert "my_field" not in config.custom_fields


class TestProject:
    """Test Project class."""
    
    def test_create_new_project(self):
        """Test creating a new project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            
            project = Project.create_new(
                project_path, 
                "Test Project", 
                TaskType.DETECTION,
                "Test description"
            )
            
            # Check project structure
            assert project.project_path == project_path
            assert project.name == "Test Project"
            assert project.task_type == TaskType.DETECTION
            assert project.description == "Test description"
            
            # Check directories exist
            assert project.dataset_dir.exists()
            assert project.model_dir.exists()
            assert project.pretrain_dir.exists()
            assert project.runs_dir.exists()
            
            # Check config file exists
            assert project.config_file.exists()
    
    def test_project_validation(self):
        """Test project validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            
            # Create valid project
            project = Project.create_new(project_path, "Test", TaskType.DETECTION)
            assert project.is_valid()
            
            # Remove a required directory
            project.dataset_dir.rmdir()
            assert not project.is_valid()
    
    def test_load_existing_project(self):
        """Test loading an existing project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            
            # Create project
            project1 = Project.create_new(project_path, "Test", TaskType.DETECTION)
            
            # Load existing project
            project2 = Project(project_path)
            assert project2.name == "Test"
            assert project2.task_type == TaskType.DETECTION


class TestProjectManager:
    """Test ProjectManager class."""
    
    def test_create_project(self):
        """Test creating a project through manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use memory database to avoid file locking issues on Windows
            with ProjectManager(":memory:") as manager:
                project_path = Path(temp_dir) / "test_project"
                
                project = manager.create_project(
                    str(project_path),
                    "Test Project",
                    TaskType.DETECTION,
                    "Test description"
                )
                
                assert project.name == "Test Project"
                assert len(manager) == 1
                
                # Check project in database
                projects = manager.get_all_projects()
                assert len(projects) == 1
                assert projects[0]["name"] == "Test Project"
    
    def test_recent_projects(self):
        """Test getting recent projects."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use memory database to avoid file locking issues on Windows
            with ProjectManager(":memory:") as manager:
                # Create multiple projects
                for i in range(3):
                    project_path = Path(temp_dir) / f"project_{i}"
                    manager.create_project(
                        str(project_path),
                        f"Project {i}",
                        TaskType.DETECTION
                    )
                
                recent = manager.get_recent_projects(limit=2)
                assert len(recent) == 2
                # Should be in reverse chronological order
                assert recent[0]["name"] == "Project 2"
                assert recent[1]["name"] == "Project 1"
    
    def test_project_removal(self):
        """Test removing projects."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use memory database to avoid file locking issues on Windows
            with ProjectManager(":memory:") as manager:
                project_path = Path(temp_dir) / "test_project"
                
                # Create project
                project = manager.create_project(
                    str(project_path),
                    "Test Project",
                    TaskType.DETECTION
                )
                
                assert len(manager) == 1
                assert project_path.exists()
                
                # Remove project (with files)
                manager.remove_project(str(project_path), delete_files=True)
                
                assert len(manager) == 0
                assert not project_path.exists()


if __name__ == "__main__":
    pytest.main([__file__])
