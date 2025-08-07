"""
Test project management functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from yoloflow.service import Project, ProjectConfig, ProjectManager


class TestProjectConfig:
    """Test ProjectConfig class."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_create_default_config(self, temp_project_dir):
        """Test creating default configuration."""
        config = ProjectConfig(temp_project_dir)
        
        assert config.project_name == temp_project_dir.name
        assert config.task_type == "detect"
        assert config.description == ""
        assert len(config.available_datasets) == 0
        assert config.current_dataset is None
    
    def test_config_persistence(self, temp_project_dir):
        """Test that configuration persists to file."""
        config = ProjectConfig(temp_project_dir)
        config.project_name = "Test Project"
        config.task_type = "classify"
        config.description = "Test Description"
        
        # Create new config instance to test loading
        config2 = ProjectConfig(temp_project_dir)
        assert config2.project_name == "Test Project"
        assert config2.task_type == "classify"
        assert config2.description == "Test Description"
    
    def test_dataset_management(self, temp_project_dir):
        """Test dataset management functions."""
        config = ProjectConfig(temp_project_dir)
        
        # Add datasets
        config.add_dataset("train_set")
        config.add_dataset("val_set")
        
        assert "train_set" in config.available_datasets
        assert "val_set" in config.available_datasets
        
        # Set current dataset
        config.current_dataset = "train_set"
        assert config.current_dataset == "train_set"
        
        # Remove dataset
        config.remove_dataset("train_set")
        assert "train_set" not in config.available_datasets
        assert config.current_dataset is None  # Should be cleared


class TestProject:
    """Test Project class."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_create_new_project(self, temp_project_dir):
        """Test creating a new project."""
        project = Project.create_new(temp_project_dir, "Test Project", "detect")
        
        assert project.name == "Test Project"
        assert project.task_type == "detect"
        assert project.path == temp_project_dir
        
        # Check folder structure
        for folder in Project.REQUIRED_FOLDERS:
            assert (temp_project_dir / folder).exists()
        
        # Check config file
        assert (temp_project_dir / "yoloflow.toml").exists()
    
    def test_load_existing_project(self, temp_project_dir):
        """Test loading an existing project."""
        # First create a project
        project1 = Project.create_new(temp_project_dir, "Test Project", "detect")
        
        # Load the same project
        project2 = Project(temp_project_dir)
        
        assert project2.name == "Test Project"
        assert project2.task_type == "detect"
        assert project2.path == temp_project_dir
    
    def test_project_paths(self, temp_project_dir):
        """Test project path properties."""
        project = Project.create_new(temp_project_dir, "Test Project")
        
        assert project.dataset_path == temp_project_dir / "dataset"
        assert project.model_path == temp_project_dir / "model"
        assert project.pretrain_path == temp_project_dir / "pretrain"
        assert project.runs_path == temp_project_dir / "runs"


class TestProjectManager:
    """Test ProjectManager class."""
    
    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for database."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_create_project_manager(self, temp_db_dir):
        """Test creating a project manager."""
        db_path = temp_db_dir / "test.db"
        manager = ProjectManager(db_path)
        
        assert manager.db_path == db_path
        assert db_path.exists()
    
    def test_create_and_manage_project(self, temp_db_dir, temp_project_dir):
        """Test creating and managing a project."""
        db_path = temp_db_dir / "test.db"
        manager = ProjectManager(db_path)
        
        # Create project
        project = manager.create_project(temp_project_dir, "Test Project", "detect")
        
        assert project.name == "Test Project"
        assert manager.get_project_count() == 1
        
        # Get all projects
        projects = manager.get_all_projects()
        assert len(projects) == 1
        assert projects[0]["name"] == "Test Project"
        assert projects[0]["path"] == str(temp_project_dir)
    
    def test_open_existing_project(self, temp_db_dir, temp_project_dir):
        """Test opening an existing project."""
        db_path = temp_db_dir / "test.db"
        manager = ProjectManager(db_path)
        
        # First create a project directly (not through manager)
        Project.create_new(temp_project_dir, "Test Project", "detect")
        
        # Open it through manager
        project = manager.open_project(temp_project_dir)
        
        assert project is not None
        assert project.name == "Test Project"
        assert manager.get_project_count() == 1
    
    def test_recent_projects(self, temp_db_dir, temp_project_dir):
        """Test getting recent projects."""
        db_path = temp_db_dir / "test.db"
        manager = ProjectManager(db_path)
        
        # Create project
        manager.create_project(temp_project_dir, "Test Project", "detect")
        
        # Get recent projects
        recent = manager.get_recent_projects()
        assert len(recent) == 1
        assert recent[0]["name"] == "Test Project"


if __name__ == "__main__":
    pytest.main([__file__])
