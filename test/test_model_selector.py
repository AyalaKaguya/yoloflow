"""
Test model selector functionality.
"""

import pytest
from yoloflow.model import ModelSelector, ModelInfo, TaskType


class TestModelInfo:
    """Test cases for ModelInfo class."""
    
    def test_model_info_creation(self):
        """Test creating ModelInfo instance."""
        model = ModelInfo(
            name="Test Model",
            filename="test.pt",
            parameters="5.2M",
            supported_tasks={TaskType.DETECTION, TaskType.CLASSIFICATION},
            description="Test model for unit testing"
        )
        
        assert model.name == "Test Model"
        assert model.filename == "test.pt"
        assert model.parameters == "5.2M"
        assert TaskType.DETECTION in model.supported_tasks
        assert TaskType.CLASSIFICATION in model.supported_tasks
        assert model.description == "Test model for unit testing"
    
    def test_supports_task(self):
        """Test task support checking."""
        model = ModelInfo(
            name="Detection Model",
            filename="detect.pt",
            parameters="2.6M",
            supported_tasks={TaskType.DETECTION},
            description="Detection only"
        )
        
        assert model.supports_task(TaskType.DETECTION)
        assert not model.supports_task(TaskType.CLASSIFICATION)
        assert not model.supports_task(TaskType.SEGMENTATION)
    
    def test_to_dict(self):
        """Test converting model to dictionary."""
        model = ModelInfo(
            name="Multi Task Model",
            filename="multi.pt",
            parameters="10.5M",
            supported_tasks={TaskType.DETECTION, TaskType.SEGMENTATION},
            description="Supports multiple tasks"
        )
        
        model_dict = model.to_dict()
        
        assert model_dict["name"] == "Multi Task Model"
        assert model_dict["filename"] == "multi.pt"
        assert model_dict["parameters"] == "10.5M"
        assert "detection" in model_dict["supported_tasks"]
        assert "segmentation" in model_dict["supported_tasks"]
        assert model_dict["description"] == "Supports multiple tasks"


class TestModelSelector:
    """Test cases for ModelSelector class."""
    
    @pytest.fixture
    def selector(self):
        """Create a fresh model selector for testing."""
        return ModelSelector()
    
    def test_initialization(self, selector):
        """Test that selector initializes with default models."""
        # Should have pre-registered models
        assert selector.get_model_count() > 0
        
        # Should support all main task types
        supported_tasks = selector.get_supported_tasks()
        assert TaskType.DETECTION in supported_tasks
        assert TaskType.CLASSIFICATION in supported_tasks
        assert TaskType.SEGMENTATION in supported_tasks
        assert TaskType.KEYPOINT in supported_tasks
        assert TaskType.ORIENTED_DETECTION in supported_tasks
    
    def test_register_model(self, selector):
        """Test registering a new model."""
        initial_count = selector.get_model_count()
        
        test_model = ModelInfo(
            name="Custom Test Model",
            filename="custom_test.pt",
            parameters="1.5M",
            supported_tasks={TaskType.CLASSIFICATION},
            description="Custom model for testing"
        )
        
        selector.register_model(test_model)
        
        # Count should increase
        assert selector.get_model_count() == initial_count + 1
        
        # Should be able to retrieve the model
        retrieved = selector.get_model_by_filename("custom_test.pt")
        assert retrieved is not None
        assert retrieved.name == "Custom Test Model"
    
    def test_register_duplicate_filename(self, selector):
        """Test that registering duplicate filename replaces existing model."""
        # Register first model
        model1 = ModelInfo(
            name="Model Version 1",
            filename="duplicate.pt",
            parameters="2.0M",
            supported_tasks={TaskType.DETECTION},
            description="First version"
        )
        selector.register_model(model1)
        initial_count = selector.get_model_count()
        
        # Register second model with same filename
        model2 = ModelInfo(
            name="Model Version 2",
            filename="duplicate.pt",
            parameters="3.0M",
            supported_tasks={TaskType.CLASSIFICATION},
            description="Second version"
        )
        selector.register_model(model2)
        
        # Count should be the same (replacement, not addition)
        assert selector.get_model_count() == initial_count
        
        # Should retrieve the newer model
        retrieved = selector.get_model_by_filename("duplicate.pt")
        assert retrieved.name == "Model Version 2"
        assert retrieved.parameters == "3.0M"
    
    def test_get_models_for_task(self, selector):
        """Test filtering models by task type."""
        detection_models = selector.get_models_for_task(TaskType.DETECTION)
        classification_models = selector.get_models_for_task(TaskType.CLASSIFICATION)
        segmentation_models = selector.get_models_for_task(TaskType.SEGMENTATION)
        
        # Should have models for each task
        assert len(detection_models) > 0
        assert len(classification_models) > 0
        assert len(segmentation_models) > 0
        
        # All detection models should support detection
        for model in detection_models:
            assert model.supports_task(TaskType.DETECTION)
        
        # All classification models should support classification
        for model in classification_models:
            assert model.supports_task(TaskType.CLASSIFICATION)
    
    def test_get_model_by_filename(self, selector):
        """Test retrieving model by filename."""
        # Test with known default model
        model = selector.get_model_by_filename("yolo11n.pt")
        assert model is not None
        assert model.filename == "yolo11n.pt"
        assert model.supports_task(TaskType.DETECTION)
        
        # Test with non-existent filename
        model = selector.get_model_by_filename("nonexistent.pt")
        assert model is None
    
    def test_get_model_by_name(self, selector):
        """Test retrieving model by display name."""
        # Test with known default model
        model = selector.get_model_by_name("YOLO 11 Nano - 检测")
        assert model is not None
        assert model.name == "YOLO 11 Nano - 检测"
        
        # Test with non-existent name
        model = selector.get_model_by_name("Non-existent Model")
        assert model is None
    
    def test_get_recommended_model(self, selector):
        """Test getting recommended models."""
        # Test preferring small models (default)
        recommended = selector.get_recommended_model(TaskType.DETECTION, prefer_small=True)
        assert recommended is not None
        assert "nano" in recommended.name.lower()
        
        # Test preferring large models
        recommended = selector.get_recommended_model(TaskType.DETECTION, prefer_small=False)
        assert recommended is not None
        # Should be a larger model (large or extra large)
        assert any(size in recommended.name.lower() for size in ["large", "extra"])
        
        # Test with unsupported task
        recommended = selector.get_recommended_model(TaskType.INSTANCE_SEGMENTATION)
        # Should still return a model (segmentation models support instance segmentation)
        assert recommended is not None
    
    def test_search_models(self, selector):
        """Test searching models."""
        # Search by task
        detection_results = selector.search_models("检测")
        assert len(detection_results) > 0
        for model in detection_results:
            assert "检测" in model.name or "检测" in model.description
        
        # Search by size
        nano_results = selector.search_models("nano")
        assert len(nano_results) > 0
        for model in nano_results:
            assert "nano" in model.name.lower() or "nano" in model.filename.lower()
        
        # Search with no results
        no_results = selector.search_models("nonexistent_keyword")
        assert len(no_results) == 0
    
    def test_get_model_count_by_task(self, selector):
        """Test counting models by task."""
        detection_count = selector.get_model_count_by_task(TaskType.DETECTION)
        classification_count = selector.get_model_count_by_task(TaskType.CLASSIFICATION)
        
        assert detection_count > 0
        assert classification_count > 0
        
        # Should have same count as direct filtering
        detection_models = selector.get_models_for_task(TaskType.DETECTION)
        assert detection_count == len(detection_models)


class TestModelSelectorWithTaskTypes:
    """Test model selector with all supported task types."""
    
    @pytest.fixture
    def selector(self):
        return ModelSelector()
    
    def test_all_task_types_supported(self, selector):
        """Test that all task types have at least one model."""
        for task_type in TaskType:
            models = selector.get_models_for_task(task_type)
            assert len(models) > 0, f"No models found for task type: {task_type.value}"
    
    def test_model_size_variations(self, selector):
        """Test that different model sizes are available."""
        detection_models = selector.get_models_for_task(TaskType.DETECTION)
        
        # Should have different sizes
        sizes_found = set()
        for model in detection_models:
            if "nano" in model.name.lower():
                sizes_found.add("nano")
            elif "small" in model.name.lower():
                sizes_found.add("small")
            elif "medium" in model.name.lower():
                sizes_found.add("medium")
            elif "large" in model.name.lower():
                sizes_found.add("large")
        
        # Should have multiple sizes
        assert len(sizes_found) >= 3, f"Expected multiple model sizes, found: {sizes_found}"
    
    def test_filename_pattern_consistency(self, selector):
        """Test that filenames follow expected patterns."""
        all_models = selector.get_all_models()
        
        for model in all_models:
            # All should end with .pt
            assert model.filename.endswith(".pt"), f"Invalid filename: {model.filename}"
            
            # Should start with yolo
            assert model.filename.startswith("yolo"), f"Unexpected filename pattern: {model.filename}"
