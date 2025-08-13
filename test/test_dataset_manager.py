"""
Test dataset manager functionality.
"""

import pytest
import tempfile
import zipfile
from pathlib import Path
import shutil

from yoloflow.model import Project, ProjectDatasetManager, DatasetInfo, DatasetType, TaskType


class TestDatasetManager:
    """Test cases for DatasetManager class."""
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            project = Project.create_new(
                project_path=project_path,
                project_name="Test Project",
                task_type=TaskType.DETECTION,
                description="Test project for dataset manager"
            )
            yield project
    
    @pytest.fixture
    def sample_dataset_folder(self):
        """Create a sample dataset folder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dataset_path = Path(temp_dir) / "sample_dataset"
            dataset_path.mkdir()
            
            # Create some sample files
            (dataset_path / "image1.jpg").write_text("fake image 1")
            (dataset_path / "image2.jpg").write_text("fake image 2")
            (dataset_path / "labels").mkdir()
            (dataset_path / "labels" / "image1.txt").write_text("0 0.5 0.5 0.2 0.2")
            (dataset_path / "labels" / "image2.txt").write_text("1 0.3 0.3 0.1 0.1")
            
            yield dataset_path
    
    @pytest.fixture
    def sample_dataset_zip(self):
        """Create a sample dataset ZIP file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "sample_dataset.zip"
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.writestr("images/image1.jpg", "fake image 1")
                zipf.writestr("images/image2.jpg", "fake image 2")
                zipf.writestr("labels/image1.txt", "0 0.5 0.5 0.2 0.2")
                zipf.writestr("labels/image2.txt", "1 0.3 0.3 0.1 0.1")
            
            yield zip_path
    
    def test_dataset_manager_initialization(self, temp_project):
        """Test dataset manager initialization."""
        dataset_manager = temp_project.dataset_manager
        
        assert isinstance(dataset_manager, ProjectDatasetManager)
        assert dataset_manager.dataset_dir.exists()
        assert dataset_manager.project_path == temp_project.project_path
        assert len(dataset_manager.datasets) == 0
    
    def test_add_dataset(self, temp_project):
        """Test adding a dataset."""
        dm = temp_project.dataset_manager
        
        # Add a dataset
        dataset_info = dm.add_dataset(
            name="test_dataset",
            dataset_type=DatasetType.DETECTION,
            description="Test dataset"
        )
        
        assert dataset_info.name == "test_dataset"
        assert dataset_info.dataset_type == DatasetType.DETECTION
        assert dataset_info.description == "Test dataset"
        assert dataset_info.path == "dataset/test_dataset"
        
        # Verify it's in the list
        datasets = dm.datasets
        assert len(datasets) == 1
        assert datasets[0].name == "test_dataset"
        
        # Test duplicate name
        with pytest.raises(ValueError, match="already exists"):
            dm.add_dataset("test_dataset")
    
    def test_get_dataset(self, temp_project):
        """Test getting dataset by name."""
        dm = temp_project.dataset_manager
        
        # Add a dataset
        dm.add_dataset("test_dataset", DatasetType.CLASSIFICATION)
        
        # Get existing dataset
        dataset = dm.get_dataset("test_dataset")
        assert dataset is not None
        assert dataset.name == "test_dataset"
        assert dataset.dataset_type == DatasetType.CLASSIFICATION
        
        # Get non-existing dataset
        dataset = dm.get_dataset("nonexistent")
        assert dataset is None
    
    def test_remove_dataset(self, temp_project):
        """Test removing a dataset."""
        dm = temp_project.dataset_manager
        
        # Add a dataset
        dm.add_dataset("test_dataset")
        assert len(dm.datasets) == 1
        
        # Remove the dataset
        dm.remove_dataset("test_dataset")
        assert len(dm.datasets) == 0
        assert dm.get_dataset("test_dataset") is None
        
        # Test removing non-existing dataset
        with pytest.raises(ValueError, match="not found"):
            dm.remove_dataset("nonexistent")
    
    def test_update_dataset(self, temp_project):
        """Test updating dataset information."""
        dm = temp_project.dataset_manager
        
        # Add a dataset
        dm.add_dataset("test_dataset", DatasetType.DETECTION, "Original description")
        
        # Update dataset
        dm.update_dataset(
            "test_dataset",
            new_name="updated_dataset",
            dataset_type=DatasetType.SEGMENTATION,
            description="Updated description"
        )
        
        # Verify updates
        dataset = dm.get_dataset("updated_dataset")
        assert dataset is not None
        assert dataset.name == "updated_dataset"
        assert dataset.dataset_type == DatasetType.SEGMENTATION
        assert dataset.description == "Updated description"
        
        # Original name should not exist
        assert dm.get_dataset("test_dataset") is None
    
    def test_import_from_folder(self, temp_project, sample_dataset_folder):
        """Test importing dataset from folder."""
        dm = temp_project.dataset_manager
        
        # Import dataset
        dataset_info = dm.import_from_folder(
            sample_dataset_folder,
            "imported_dataset",
            DatasetType.DETECTION,
            "Imported from folder"
        )
        
        assert dataset_info.name == "imported_dataset"
        assert dataset_info.dataset_type == DatasetType.DETECTION
        
        # Verify files were copied
        dataset_path = dm.get_dataset_path("imported_dataset")
        assert dataset_path.exists()
        assert (dataset_path / "image1.jpg").exists()
        assert (dataset_path / "image2.jpg").exists()
        assert (dataset_path / "labels" / "image1.txt").exists()
        
        # Verify in dataset list
        assert len(dm.datasets) == 1
        assert dm.get_dataset("imported_dataset") is not None
    
    def test_import_from_zip(self, temp_project, sample_dataset_zip):
        """Test importing dataset from ZIP file."""
        dm = temp_project.dataset_manager
        
        # Import dataset
        dataset_info = dm.import_from_zip(
            sample_dataset_zip,
            "imported_zip_dataset",
            DatasetType.DETECTION,
            "Imported from ZIP"
        )
        
        assert dataset_info.name == "imported_zip_dataset"
        
        # Verify files were extracted
        dataset_path = dm.get_dataset_path("imported_zip_dataset")
        assert dataset_path.exists()
        assert (dataset_path / "images" / "image1.jpg").exists()
        assert (dataset_path / "images" / "image2.jpg").exists()
        assert (dataset_path / "labels" / "image1.txt").exists()
    
    def test_import_dataset_auto_detect(self, temp_project, sample_dataset_folder, sample_dataset_zip):
        """Test auto-detection of import method."""
        dm = temp_project.dataset_manager
        
        # Import from folder (auto-detect)
        dataset1 = dm.import_dataset(sample_dataset_folder, "folder_dataset")
        assert dataset1.name == "folder_dataset"
        
        # Import from ZIP (auto-detect)
        dataset2 = dm.import_dataset(sample_dataset_zip, "zip_dataset")
        assert dataset2.name == "zip_dataset"
        
        # Test unsupported file type
        with tempfile.TemporaryDirectory() as temp_dir:
            txt_file = Path(temp_dir) / "dataset.txt"
            txt_file.write_text("not a dataset")
            
            with pytest.raises(ValueError, match="Unsupported source type"):
                dm.import_dataset(txt_file, "invalid_dataset")
    
    def test_current_dataset(self, temp_project):
        """Test current dataset functionality."""
        dm = temp_project.dataset_manager
        
        # Initially no current dataset
        assert dm.current_dataset is None
        
        # Add datasets
        dm.add_dataset("dataset1")
        dm.add_dataset("dataset2")
        
        # Set current dataset
        dm.current_dataset = "dataset1"
        current = dm.current_dataset
        assert current is not None
        assert current.name == "dataset1"
        
        # Set to None
        dm.current_dataset = None
        assert dm.current_dataset is None
        
        # Test invalid dataset name
        with pytest.raises(ValueError, match="not found"):
            dm.current_dataset = "nonexistent"
    
    def test_list_dataset_files(self, temp_project, sample_dataset_folder):
        """Test listing dataset files."""
        dm = temp_project.dataset_manager
        
        # Import dataset
        dm.import_from_folder(sample_dataset_folder, "test_dataset")
        
        # List files
        files = dm.list_dataset_files("test_dataset")
        assert len(files) == 4  # 2 images + 2 label files
        
        file_names = [f.name for f in files]
        assert "image1.jpg" in file_names
        assert "image2.jpg" in file_names
        assert "image1.txt" in file_names
        assert "image2.txt" in file_names
    
    def test_default_dataset_type(self, temp_project):
        """Test that default dataset type matches project task type."""
        dm = temp_project.dataset_manager
        
        # Project is DETECTION type
        assert temp_project.task_type == TaskType.DETECTION
        
        # Add dataset without specifying type
        dataset_info = dm.add_dataset("test_dataset")
        assert dataset_info.dataset_type == DatasetType.DETECTION
    
    def test_migration_from_simple_format(self, temp_project):
        """Test migration from old simple dataset format."""
        dm = temp_project.dataset_manager
        
        # Simulate old format by directly adding to simple list
        temp_project.config.add_dataset("old_dataset1")
        temp_project.config.add_dataset("old_dataset2")
        temp_project.config.save()
        
        # Clear detailed format to simulate old config
        temp_project.config._config_data["datasets"]["detailed"] = []
        
        # Reinitialize dataset manager to trigger migration
        dm_new = ProjectDatasetManager(temp_project.project_path, temp_project.config)
        
        # Check that datasets were migrated
        datasets = dm_new.datasets
        assert len(datasets) == 2
        
        dataset_names = [d.name for d in datasets]
        assert "old_dataset1" in dataset_names
        assert "old_dataset2" in dataset_names
        
        # All should have default project task type
        for dataset in datasets:
            assert dataset.dataset_type == DatasetType.DETECTION
