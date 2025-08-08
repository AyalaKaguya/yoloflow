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
        
        # Check that plan manager is accessible through project
        assert hasattr(project, 'plan_manager')
        assert project.plan_manager is not None
        
        # Test basic functionality
        pretrained_models = project.model_manager.get_pretrained_models()
        assert isinstance(pretrained_models, list)
        assert len(pretrained_models) == 0  # Should be empty for new project
        
        trained_models = project.model_manager.get_trained_models()
        assert isinstance(trained_models, list)
        assert len(trained_models) == 0  # Should be empty for new project
        
        # Test plan management
        plans = project.plan_manager.get_all_plans()
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
        
        # Check that plan manager is properly initialized
        assert hasattr(project2, 'plan_manager')
        assert project2.plan_manager is not None
        assert project2.plan_manager.task_type == TaskType.CLASSIFICATION
        assert project2.plan_manager.config == project2.config
        
        # Test that both projects have the same configuration
        assert project1.config.task_type == project2.config.task_type
        assert project1.name == project2.name


def test_project_plan_manager_integration():
    """Test plan manager integration at project level."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "plan_test_project"
        
        # Create a project
        project = Project.create_new(
            project_path=project_path,
            project_name="Plan Test Project",
            task_type=TaskType.DETECTION,
            description="Test project for plan management"
        )
        
        # Test direct plan manager access
        assert hasattr(project, 'plan_manager')
        assert project.plan_manager is not None
        
        # Create a training plan
        plan = project.plan_manager.create_plan("Test Plan")
        assert plan.name == "Test Plan"
        assert plan.task_type == TaskType.DETECTION
        
        # Test plan retrieval
        plans = project.plan_manager.get_all_plans()
        assert len(plans) == 1
        assert plans[0].name == "Test Plan"
        
        # Test project summary includes plan information
        summary = project.get_project_summary()
        assert summary["training_plans"] == 1
        assert summary["completed_plans"] == 0
        assert summary["pending_plans"] == 1
