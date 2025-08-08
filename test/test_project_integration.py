"""
Test project integration with model managers.
"""

import tempfile
from pathlib import Path

from yoloflow.model.enums import TaskType
from yoloflow.model.project import Project


def test_project_integration():
    """Test that Project class properly integrates with model managers."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        
        # Create a new project
        project = Project.create_new(
            project_path=project_path,
            project_name="Test Project",
            task_type=TaskType.DETECTION,
            description="Test project for integration"
        )
        
        # Check that model manager is properly initialized
        assert hasattr(project, 'model_manager')
        assert project.model_manager is not None
        assert project.model_manager.task_type == TaskType.DETECTION
        assert project.model_manager.config == project.config
        
        # Check that plan manager is accessible through model manager
        assert hasattr(project.model_manager, 'plan_manager')
        assert project.model_manager.plan_manager is not None
        
        # Test basic functionality
        pretrained_models = project.model_manager.get_pretrained_models()
        assert isinstance(pretrained_models, list)
        assert len(pretrained_models) == 0  # Should be empty for new project
        
        trained_models = project.model_manager.get_trained_models()
        assert isinstance(trained_models, list)
        assert len(trained_models) == 0  # Should be empty for new project
        
        # Test plan management
        plans = project.model_manager.get_all_training_plans()
        assert isinstance(plans, list)
        assert len(plans) == 0  # Should be empty for new project


def test_project_load_existing():
    """Test loading existing project with model managers."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        
        # Create a project
        project1 = Project.create_new(
            project_path=project_path,
            project_name="Test Project",
            task_type=TaskType.CLASSIFICATION,
            description="Test project"
        )
        
        # Load the same project
        project2 = Project(project_path)
        
        # Check that model manager is properly initialized
        assert hasattr(project2, 'model_manager')
        assert project2.model_manager is not None
        assert project2.model_manager.task_type == TaskType.CLASSIFICATION
        assert project2.model_manager.config == project2.config
        
        # Test that both projects have the same configuration
        assert project1.config.task_type == project2.config.task_type
        assert project1.name == project2.name
