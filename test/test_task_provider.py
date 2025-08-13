"""
Test task type provider functionality.
"""

import pytest
from yoloflow.model import (
    TaskTypeProvider, TaskInfo, TaskType
)


class TestTaskInfo:
    """Test cases for TaskInfo class."""
    
    def test_task_info_creation(self):
        """Test creating TaskInfo instance."""
        task_info = TaskInfo(
            task_type=TaskType.DETECTION,
            name="目标检测",
            description="检测图像中的对象",
            example_image="detection_example.jpg"
        )
        
        assert task_info.task_type == TaskType.DETECTION
        assert task_info.name == "目标检测"
        assert task_info.description == "检测图像中的对象"
        assert task_info.example_image == "detection_example.jpg"
    
    def test_task_info_without_image(self):
        """Test creating TaskInfo without example image."""
        task_info = TaskInfo(
            task_type=TaskType.CLASSIFICATION,
            name="图像分类",
            description="分类图像内容"
        )
        
        assert task_info.example_image is None
    
    def test_to_dict(self):
        """Test converting TaskInfo to dictionary."""
        task_info = TaskInfo(
            task_type=TaskType.SEGMENTATION,
            name="语义分割",
            description="像素级分割",
            example_image="seg_example.png"
        )
        
        task_dict = task_info.to_dict()
        
        assert task_dict["task_type"] == "segmentation"
        assert task_dict["name"] == "语义分割"
        assert task_dict["description"] == "像素级分割"
        assert task_dict["example_image"] == "seg_example.png"
    
    def test_from_dict(self):
        """Test creating TaskInfo from dictionary."""
        data = {
            "task_type": "keypoint",
            "name": "关键点检测",
            "description": "检测关键点位置",
            "example_image": "keypoint_example.jpg"
        }
        
        task_info = TaskInfo.from_dict(data)
        
        assert task_info.task_type == TaskType.KEYPOINT
        assert task_info.name == "关键点检测"
        assert task_info.description == "检测关键点位置"
        assert task_info.example_image == "keypoint_example.jpg"


class TestTaskTypeProvider:
    """Test cases for TaskTypeProvider class."""
    
    @pytest.fixture
    def provider(self):
        """Create a fresh task type provider for testing."""
        return TaskTypeProvider()
    
    def test_initialization(self, provider):
        """Test that provider initializes with default tasks."""
        # Should have all default task types
        assert provider.get_task_count() == 6  # All supported task types
        
        # Should have all main task types
        expected_types = [
            TaskType.CLASSIFICATION,
            TaskType.DETECTION,
            TaskType.SEGMENTATION,
            TaskType.INSTANCE_SEGMENTATION,
            TaskType.KEYPOINT,
            TaskType.ORIENTED_DETECTION
        ]
        
        registered_types = provider.get_task_types()
        for task_type in expected_types:
            assert task_type in registered_types
    
    def test_get_task_info(self, provider):
        """Test getting task information."""
        # Test existing task
        detection_info = provider.get_task_info(TaskType.DETECTION)
        assert detection_info is not None
        assert detection_info.task_type == TaskType.DETECTION
        assert "检测" in detection_info.name
        assert len(detection_info.description) > 0
        
        # Test all default tasks have info
        for task_type in TaskType:
            task_info = provider.get_task_info(task_type)
            assert task_info is not None
            assert task_info.task_type == task_type
    
    def test_register_task(self, provider):
        """Test registering a new task."""
        initial_count = provider.get_task_count()
        
        # Create a custom task (this should replace existing one)
        custom_task = TaskInfo(
            task_type=TaskType.DETECTION,  # Replace existing detection
            name="自定义检测",
            description="自定义的检测任务",
            example_image="custom_detection.jpg"
        )
        
        provider.register_task(custom_task)
        
        # Count should be the same (replacement)
        assert provider.get_task_count() == initial_count
        
        # Should retrieve the new task info
        retrieved = provider.get_task_info(TaskType.DETECTION)
        assert retrieved.name == "自定义检测"
        assert retrieved.description == "自定义的检测任务"
        assert retrieved.example_image == "custom_detection.jpg"
    
    def test_get_all_tasks(self, provider):
        """Test getting all tasks in order."""
        all_tasks = provider.get_all_tasks()
        
        # Should have all tasks
        assert len(all_tasks) == 6
        
        # Should maintain expected order
        expected_order = [
            TaskType.CLASSIFICATION,
            TaskType.DETECTION,
            TaskType.SEGMENTATION,
            TaskType.INSTANCE_SEGMENTATION,
            TaskType.KEYPOINT,
            TaskType.ORIENTED_DETECTION
        ]
        
        for i, expected_type in enumerate(expected_order):
            assert all_tasks[i].task_type == expected_type
    
    def test_get_task_names(self, provider):
        """Test getting task display names."""
        names = provider.get_task_names()
        
        assert len(names) == 6
        assert "图像分类" in names
        assert "目标检测" in names
        assert "语义分割" in names
    
    def test_search_tasks(self, provider):
        """Test searching tasks."""
        # Search by name
        detection_results = provider.search_tasks("检测")
        assert len(detection_results) >= 2  # Detection and oriented detection
        for result in detection_results:
            assert "检测" in result.name or "检测" in result.description
        
        # Search by description keyword
        pixel_results = provider.search_tasks("像素")
        assert len(pixel_results) > 0
        for result in pixel_results:
            assert "像素" in result.description
        
        # Search with no results
        no_results = provider.search_tasks("不存在的关键词")
        assert len(no_results) == 0
    
    def test_is_task_registered(self, provider):
        """Test checking if task is registered."""
        # All default tasks should be registered
        for task_type in TaskType:
            assert provider.is_task_registered(task_type)
    
    def test_get_task_by_name(self, provider):
        """Test getting task by display name."""
        # Test existing task
        task_info = provider.get_task_by_name("图像分类")
        assert task_info is not None
        assert task_info.task_type == TaskType.CLASSIFICATION
        
        # Test non-existing name
        task_info = provider.get_task_by_name("不存在的任务")
        assert task_info is None
    
    def test_update_task_example_image(self, provider):
        """Test updating task example image."""
        # Update example image
        provider.update_task_example_image(TaskType.CLASSIFICATION, "new_class_example.jpg")
        
        # Verify update
        task_info = provider.get_task_info(TaskType.CLASSIFICATION)
        assert task_info.example_image == "new_class_example.jpg"
        
        # Test updating non-existing task (should not raise error)
        provider.update_task_example_image(TaskType.DETECTION, "detection_example.jpg")
        detection_info = provider.get_task_info(TaskType.DETECTION)
        assert detection_info.example_image == "detection_example.jpg"
    
    def test_remove_task(self, provider):
        """Test removing a task."""
        initial_count = provider.get_task_count()
        
        # Remove a task
        provider.remove_task(TaskType.KEYPOINT)
        
        # Count should decrease
        assert provider.get_task_count() == initial_count - 1
        
        # Task should not be registered
        assert not provider.is_task_registered(TaskType.KEYPOINT)
        assert provider.get_task_info(TaskType.KEYPOINT) is None

