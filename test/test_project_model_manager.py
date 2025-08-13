"""
Tests for project model manager functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open

from yoloflow.model import (
    ProjectModelManager,
    ProjectPlanManager,
    PlanContext,
    DatasetTarget,
    PlanDatasetConfig,
    TrainingParameters,
    ValidationParameters,
    TrainingResults,
    TaskType
)
from yoloflow.model.project import ProjectConfig


def create_test_config(project_path: Path, task_type: TaskType = TaskType.DETECTION) -> ProjectConfig:
    """Create a test project configuration."""
    config_path = project_path / "yoloflow.toml"
    config = ProjectConfig(config_path)
    config.project_name = "Test Project"
    config.task_type = task_type
    config.description = "Test project"
    return config


class TestDatasetConfig:
    """Test DatasetConfig class."""
    
    def test_create_dataset_config(self):
        """Test creating dataset config."""
        config = PlanDatasetConfig("test_dataset", DatasetTarget.TRAIN)
        assert config.name == "test_dataset"
        assert config.target == DatasetTarget.TRAIN
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        config = PlanDatasetConfig("test_dataset", DatasetTarget.VAL)
        data = config.to_dict()
        assert data == {
            "name": "test_dataset",
            "target": "val"
        }
    
    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {"name": "test_dataset", "target": "test"}
        config = PlanDatasetConfig.from_dict(data)
        assert config.name == "test_dataset"
        assert config.target == DatasetTarget.TEST


class TestTrainingParameters:
    """Test TrainingParameters class."""
    
    def test_default_parameters(self):
        """Test default training parameters."""
        params = TrainingParameters()
        assert params.epochs == 100
        assert params.learning_rate == 0.01
        assert params.input_size == 640
        assert params.batch_size == 16
        assert params.extra_params == {}
    
    def test_custom_parameters(self):
        """Test custom training parameters."""
        params = TrainingParameters(
            epochs=200,
            learning_rate=0.001,
            extra_params={"weight_decay": 0.0005}
        )
        assert params.epochs == 200
        assert params.learning_rate == 0.001
        assert params.extra_params["weight_decay"] == 0.0005
    
    def test_serialization(self):
        """Test parameter serialization."""
        params = TrainingParameters(epochs=50, extra_params={"test": True})
        data = params.to_dict()
        restored = TrainingParameters.from_dict(data)
        
        assert restored.epochs == 50
        assert restored.extra_params["test"] is True


class TestValidationParameters:
    """Test ValidationParameters class."""
    
    def test_default_parameters(self):
        """Test default validation parameters."""
        params = ValidationParameters()
        assert params.confidence_threshold == 0.25
        assert params.iou_threshold == 0.45
    
    def test_serialization(self):
        """Test parameter serialization."""
        params = ValidationParameters(confidence_threshold=0.5, iou_threshold=0.6)
        data = params.to_dict()
        restored = ValidationParameters.from_dict(data)
        
        assert restored.confidence_threshold == 0.5
        assert restored.iou_threshold == 0.6


class TestTrainingResults:
    """Test TrainingResults class."""
    
    def test_default_results(self):
        """Test default training results."""
        results = TrainingResults()
        assert results.best_model is None
        assert results.latest_model is None
    
    def test_with_models(self):
        """Test results with model paths."""
        results = TrainingResults("best.pt", "latest.pt")
        assert results.best_model == "best.pt"
        assert results.latest_model == "latest.pt"
    
    def test_serialization(self):
        """Test results serialization."""
        results = TrainingResults("best.pt", "latest.pt")
        data = results.to_dict()
        restored = TrainingResults.from_dict(data)
        
        assert restored.best_model == "best.pt"
        assert restored.latest_model == "latest.pt"


class TestPlanContext:
    """Test PlanContext class."""
    
    def test_create_new_plan(self):
        """Test creating a new plan."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            plan = PlanContext.create_new(
                "test_plan",
                project_path,
                TaskType.CLASSIFICATION,
                "yolo11n-cls.pt"
            )
            
            assert plan.name == "test_plan"
            assert plan.project_path == project_path
            assert plan.task_type == TaskType.CLASSIFICATION
            assert plan.pretrained_model == "yolo11n-cls.pt"
            assert len(plan.plan_id) == 36  # UUID length
    
    def test_save_and_load_plan(self):
        """Test saving and loading plan."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create and save plan
            plan = PlanContext.create_new("test_plan", project_path, TaskType.DETECTION)
            plan.add_dataset("dataset1", DatasetTarget.TRAIN)
            plan.update_training_params(epochs=50, learning_rate=0.001)
            plan.save()
            
            # Load plan
            loaded_plan = PlanContext.load_from_file(plan.plan_file)
            
            assert loaded_plan.name == "test_plan"
            assert loaded_plan.task_type == TaskType.DETECTION
            assert len(loaded_plan.datasets) == 1
            assert loaded_plan.datasets[0].name == "dataset1"
            assert loaded_plan.training_params.epochs == 50
    
    def test_add_remove_datasets(self):
        """Test adding and removing datasets."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            plan = PlanContext.create_new("test_plan", project_path, TaskType.DETECTION)
            
            # Add datasets
            plan.add_dataset("train_data", DatasetTarget.TRAIN)
            plan.add_dataset("val_data", DatasetTarget.VAL)
            
            assert len(plan.datasets) == 2
            
            # Remove dataset
            plan.remove_dataset("train_data")
            assert len(plan.datasets) == 1
            assert plan.datasets[0].name == "val_data"
    
    def test_update_parameters(self):
        """Test updating parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            plan = PlanContext.create_new("test_plan", project_path, TaskType.DETECTION)
            
            # Update training parameters
            plan.update_training_params(epochs=200, custom_param="test")
            assert plan.training_params.epochs == 200
            assert plan.training_params.extra_params["custom_param"] == "test"
            
            # Update validation parameters
            plan.update_validation_params(confidence_threshold=0.7)
            assert plan.validation_params.confidence_threshold == 0.7
    
    def test_set_results(self):
        """Test setting training results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            plan = PlanContext.create_new("test_plan", project_path, TaskType.DETECTION)
            
            plan.set_results(best_model="best.pt", latest_model="latest.pt")
            assert plan.results.best_model == "best.pt"
            assert plan.results.latest_model == "latest.pt"
            assert plan.has_results() is True
    
    def test_get_dataset_by_target(self):
        """Test getting datasets by target."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            plan = PlanContext.create_new("test_plan", project_path, TaskType.DETECTION)
            
            plan.add_dataset("train1", DatasetTarget.TRAIN)
            plan.add_dataset("train2", DatasetTarget.TRAIN)
            plan.add_dataset("val1", DatasetTarget.VAL)
            
            train_datasets = plan.get_dataset_by_target(DatasetTarget.TRAIN)
            val_datasets = plan.get_dataset_by_target(DatasetTarget.VAL)
            
            assert len(train_datasets) == 2
            assert len(val_datasets) == 1
    
    def test_delete_plan(self):
        """Test deleting plan file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            plan = PlanContext.create_new("test_plan", project_path, TaskType.DETECTION)
            plan.save()
            
            assert plan.plan_file.exists()
            plan.delete()
            assert not plan.plan_file.exists()


class TestProjectPlanManager:
    """Test ProjectPlanManager class."""
    
    def test_create_plan_manager(self):
        """Test creating plan manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectPlanManager(project_path, config)

            assert manager.project_path == project_path
            assert manager.task_type == TaskType.DETECTION
            assert manager.plan_dir.exists()
    
    def test_create_plan(self):
        """Test creating a plan."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectPlanManager(project_path, config)
            
            plan = manager.create_plan("test_plan", "yolo11n.pt")
            
            assert plan.name == "test_plan"
            assert plan.pretrained_model == "yolo11n.pt"
            assert manager.get_plan_count() == 1
    
    def test_duplicate_plan_name(self):
        """Test creating plan with duplicate name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectPlanManager(project_path, config)
            
            manager.create_plan("test_plan")
            
            with pytest.raises(ValueError, match="already exists"):
                manager.create_plan("test_plan")
    
    def test_get_plan_by_id_and_name(self):
        """Test getting plan by ID and name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectPlanManager(project_path, config)
            
            plan = manager.create_plan("test_plan")
            
            # Get by ID
            found_plan = manager.get_plan(plan.plan_id)
            assert found_plan is not None
            assert found_plan.name == "test_plan"
            
            # Get by name
            found_plan = manager.get_plan_by_name("test_plan")
            assert found_plan is not None
            assert found_plan.plan_id == plan.plan_id
    
    def test_delete_plan(self):
        """Test deleting a plan."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectPlanManager(project_path, config)
            
            plan = manager.create_plan("test_plan")
            plan_id = plan.plan_id
            
            assert manager.get_plan_count() == 1
            
            success = manager.delete_plan(plan_id)
            assert success is True
            assert manager.get_plan_count() == 0
            assert manager.get_plan(plan_id) is None
    
    def test_get_plans_by_status(self):
        """Test getting plans by result status."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectPlanManager(project_path, config)
            
            # Create plans
            plan1 = manager.create_plan("plan1")
            plan2 = manager.create_plan("plan2")
            
            # Set results for plan1
            plan1.set_results(best_model="best.pt")
            plan1.save()
            
            # Check status groups
            completed = manager.get_plans_by_status(True)
            pending = manager.get_plans_by_status(False)
            
            assert len(completed) == 1
            assert len(pending) == 1
            assert completed[0].plan_id == plan1.plan_id
    
    def test_search_plans(self):
        """Test searching plans by name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectPlanManager(project_path, config)
            
            manager.create_plan("detection_plan")
            manager.create_plan("classification_plan")
            manager.create_plan("segmentation_plan")
            
            results = manager.search_plans("detection")
            assert len(results) == 1
            assert results[0].name == "detection_plan"
            
            results = manager.search_plans("plan")
            assert len(results) == 3


class TestProjectModelManager:
    """Test ProjectModelManager class."""
    
    def test_create_model_manager(self):
        """Test creating model manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectModelManager(project_path, config)
            
            assert manager.project_path == project_path
            assert manager.task_type == TaskType.DETECTION
            assert manager.pretrain_dir.exists()
            assert manager.model_dir.exists()
            # Plan manager is no longer part of model manager
    
    def test_get_pretrained_models(self):
        """Test getting pretrained models."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectModelManager(project_path, config)
            
            # Create fake model files
            (manager.pretrain_dir / "yolo11n.pt").touch()
            (manager.pretrain_dir / "yolo11s.pt").touch()
            (manager.pretrain_dir / "not_model.txt").touch()  # Should be ignored
            
            models = manager.get_pretrained_models()
            assert len(models) == 2
            
            # Check that we get ProjectModelInfo objects
            model_filenames = [model.filename for model in models]
            assert "yolo11n.pt" in model_filenames
            assert "yolo11s.pt" in model_filenames
            assert "not_model.txt" not in model_filenames
            
            # Check that models are ProjectModelInfo objects
            for model in models:
                assert hasattr(model, 'name')
                assert hasattr(model, 'filename')
                assert hasattr(model, 'description')
                assert hasattr(model, 'parameters')
                assert hasattr(model, 'task_type')
                assert hasattr(model, 'source')
    
    def test_get_trained_models(self):
        """Test getting trained models."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectModelManager(project_path, config)
            
            # Create fake model files
            (manager.model_dir / "best.pt").touch()
            (manager.model_dir / "latest.pt").touch()
            
            models = manager.get_trained_models()
            assert len(models) == 2
            
            # Check that we get ProjectModelInfo objects
            model_filenames = [model.filename for model in models]
            assert "best.pt" in model_filenames
            assert "latest.pt" in model_filenames
            
            # Check that models are ProjectModelInfo objects
            for model in models:
                assert hasattr(model, 'name')
                assert hasattr(model, 'filename')
                assert hasattr(model, 'description')
                assert hasattr(model, 'parameters')
                assert hasattr(model, 'task_type')
                assert hasattr(model, 'source')
    
    def test_add_pretrained_model(self):
        """Test adding pretrained model."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectModelManager(project_path, config)
            
            # Create source model file
            source_file = Path(temp_dir) / "source_model.pt"
            source_file.write_text("fake model data")
            
            # Add model with new API
            model_info = manager.add_pretrained_model(
                source_path=source_file,
                model_name="Test Model",
                description="A test model",
                parameters="2600000"
            )
            assert model_info.filename == "source_model.pt"
            
            # Check file was copied
            target_file = manager.pretrain_dir / "source_model.pt"
            assert target_file.exists()
            assert target_file.read_text() == "fake model data"
            
            # Check model info was saved
            model_info = config.get_model_info("source_model.pt")
            assert model_info is not None
            assert model_info.name == "Test Model"
            assert model_info.description == "A test model"
            assert model_info.parameters == "2600000"
    
    def test_add_pretrained_model_custom_name(self):
        """Test adding pretrained model with custom name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectModelManager(project_path, config)
            
            # Create source model file
            source_file = Path(temp_dir) / "source_model.pt"
            source_file.write_text("fake model data")
            
            # Add model with custom filename
            model_name = manager.add_pretrained_model(
                source_path=source_file,
                model_name="Custom Model",
                filename="custom_model.pt"
            )
            assert model_name.filename == "custom_model.pt"
            
            # Check file exists with custom name
            target_file = manager.pretrain_dir / "custom_model.pt"
            assert target_file.exists()
    
    def test_add_duplicate_pretrained_model(self):
        """Test adding duplicate pretrained model."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectModelManager(project_path, config)
            
            # Create existing model
            (manager.pretrain_dir / "existing.pt").touch()
            
            # Create source model file
            source_file = Path(temp_dir) / "existing.pt"
            source_file.write_text("fake model data")
            
            # Try to add duplicate
            with pytest.raises(ValueError, match="already exists"):
                manager.add_pretrained_model(
                    source_path=source_file,
                    model_name="Test Model"
                )
    
    def test_remove_pretrained_model(self):
        """Test removing pretrained model."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectModelManager(project_path, config)
            
            # Create model file
            model_file = manager.pretrain_dir / "test_model.pt"
            model_file.touch()
            
            # Remove model
            success = manager.remove_pretrained_model("test_model.pt")
            assert success is True
            assert not model_file.exists()
            
            # Try to remove non-existent model
            success = manager.remove_pretrained_model("non_existent.pt")
            assert success is False
    
    def test_get_model_paths(self):
        """Test getting model file paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectModelManager(project_path, config)
            
            # Create model files
            pretrained_file = manager.pretrain_dir / "pretrained.pt"
            pretrained_file.touch()
            trained_file = manager.model_dir / "trained.pt"
            trained_file.touch()
            
            # Test existing models
            assert manager.get_pretrained_model_path("pretrained.pt") == pretrained_file
            assert manager.get_trained_model_path("trained.pt") == trained_file
            
            # Test non-existent models
            assert manager.get_pretrained_model_path("non_existent.pt") is None
            assert manager.get_trained_model_path("non_existent.pt") is None
    
    def test_model_manager_basic_functionality(self):
        """Test basic model manager functionality without plan integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectModelManager(project_path, config)
            
            # Test basic properties
            assert manager.project_path == project_path
            assert manager.task_type == TaskType.DETECTION
            assert manager.config == config
            
            # Test directories exist
            assert manager.pretrain_dir.exists()
            assert manager.model_dir.exists()
            
            # Test empty lists initially
            assert len(manager.get_pretrained_models()) == 0
            assert len(manager.get_trained_models()) == 0
    
    def test_get_model_summary(self):
        """Test getting model summary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectModelManager(project_path, config)
            
            # Create model files
            (manager.pretrain_dir / "pretrained1.pt").touch()
            (manager.pretrain_dir / "pretrained2.pt").touch()
            (manager.model_dir / "trained1.pt").touch()
            
            summary = manager.get_model_summary()
            
            assert summary["pretrained_models"] == 2
            assert summary["trained_models"] == 1
            # No longer includes plan information
            assert "training_plans" not in summary
            assert "completed_plans" not in summary
            assert "pending_plans" not in summary


class TestNewModelManagerAPI:
    """Test the new enhanced model manager API."""
    
    def test_add_trained_model(self):
        """Test adding trained model with detailed info."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectModelManager(project_path, config)
            
            # Create source model file
            source_file = Path(temp_dir) / "trained_model.pt"
            source_file.write_text("fake trained model data")
            
            # Add trained model
            model_name = manager.add_trained_model(
                source_path=source_file,
                plan_name="Test Plan",
                model_name="Trained YOLO11",
                description="Model trained on custom dataset",
                parameters="2600000"
            )
            assert model_name == "trained_model.pt"
            
            # Check file was copied to model directory
            target_file = manager.model_dir / "trained_model.pt"
            assert target_file.exists()
            assert target_file.read_text() == "fake trained model data"
            
            # Check model info
            model_info = config.get_model_info("trained_model.pt")
            assert model_info is not None
            assert model_info.name == "Trained YOLO11"
            assert model_info.source == "plan_created"
            assert model_info.parameters == "2600000"
    
    def test_add_model_from_info(self):
        """Test adding model using ProjectModelInfo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectModelManager(project_path, config)
            
            # Create source model file
            source_file = Path(temp_dir) / "custom_model.pt"
            source_file.write_text("custom model data")
            
            # Create model info
            from yoloflow.model.project.project_model_info import ProjectModelInfo
            model_info = ProjectModelInfo(
                name="Custom YOLO Model",
                filename="custom_yolo.pt",
                description="A custom trained model",
                parameters="5000000",
                task_type=TaskType.DETECTION,
                source="plan_created"
            )
            
            # Add model using info
            result_name = manager.add_model_from_info(model_info, source_file)
            assert result_name.filename == "custom_yolo.pt"
            
            # Check file was copied to correct directory (model dir for plan_created)
            target_file = manager.model_dir / "custom_yolo.pt"
            assert target_file.exists()
            
            # Check model info was saved
            saved_info = config.get_model_info("custom_yolo.pt")
            assert saved_info is not None
            assert saved_info.name == "Custom YOLO Model"
            assert saved_info.parameters == "5000000"
    
    def test_enhanced_model_summary(self):
        """Test the enhanced model summary with detailed info."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            config = create_test_config(project_path, TaskType.DETECTION)
            manager = ProjectModelManager(project_path, config)
            
            # Add pretrained model
            source_file1 = Path(temp_dir) / "pretrained.pt"
            source_file1.write_text("pretrained data")
            manager.add_pretrained_model(
                source_path=source_file1,
                model_name="YOLO11n",
                parameters="2600000"
            )
            
            # Add trained model
            source_file2 = Path(temp_dir) / "trained.pt"
            source_file2.write_text("trained data")
            manager.add_trained_model(
                source_path=source_file2,
                plan_name="Training Plan",
                model_name="Custom Trained Model",
                parameters="2700000"
            )
            
            # Get summary
            summary = manager.get_model_summary()
            
            assert summary["pretrained_models"] == 1
            assert summary["trained_models"] == 1
            assert len(summary["model_details"]) == 2
            assert "available_models" in summary
            
            # Check model details
            model_details = summary["model_details"]
            pretrained_detail = next(m for m in model_details if m["source"] == "imported")
            trained_detail = next(m for m in model_details if m["source"] == "plan_created")
            
            assert pretrained_detail["name"] == "YOLO11n"
            assert pretrained_detail["parameters"] == "2600000"
            assert trained_detail["name"] == "Custom Trained Model"
            assert trained_detail["parameters"] == "2700000"
