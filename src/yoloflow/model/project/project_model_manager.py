"""
Manager for all models within a project.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..enums import TaskType
from .plan_context import PlanContext
from .project_plan_manager import ProjectPlanManager


class ProjectModelManager:
    """
    Manager for all models within a project.
    
    Handles both pretrained models and trained models, as well as
    training plans through the ProjectPlanManager.
    """
    
    def __init__(self, project_path: Path, task_type: TaskType):
        """
        Initialize project model manager.
        
        Args:
            project_path: Path to the project directory
            task_type: Project task type
        """
        self.project_path = Path(project_path)
        self.task_type = task_type
        self.pretrain_dir = self.project_path / "pretrain"
        self.model_dir = self.project_path / "model"
        
        # Ensure directories exist
        self.pretrain_dir.mkdir(exist_ok=True)
        self.model_dir.mkdir(exist_ok=True)
        
        # Initialize plan manager
        self.plan_manager = ProjectPlanManager(project_path, task_type)
    
    def get_pretrained_models(self) -> List[str]:
        """
        Get list of pretrained model files.
        
        Returns:
            List of pretrained model filenames
        """
        models = []
        if self.pretrain_dir.exists():
            for model_file in self.pretrain_dir.glob("*.pt"):
                models.append(model_file.name)
        return sorted(models)
    
    def get_trained_models(self) -> List[str]:
        """
        Get list of trained model files.
        
        Returns:
            List of trained model filenames
        """
        models = []
        if self.model_dir.exists():
            for model_file in self.model_dir.glob("*.pt"):
                models.append(model_file.name)
        return sorted(models)
    
    def add_pretrained_model(self, source_path: Union[str, Path], model_name: Optional[str] = None) -> str:
        """
        Add a pretrained model to the project.
        
        Args:
            source_path: Path to source model file
            model_name: Optional custom name for the model
            
        Returns:
            Name of the added model file
            
        Raises:
            FileNotFoundError: If source file doesn't exist
            ValueError: If model already exists
        """
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source model file not found: {source_path}")
        
        # Determine target filename
        if model_name:
            if not model_name.endswith('.pt'):
                model_name += '.pt'
            target_name = model_name
        else:
            target_name = source_path.name
        
        target_path = self.pretrain_dir / target_name
        
        # Check if model already exists
        if target_path.exists():
            raise ValueError(f"Pretrained model '{target_name}' already exists")
        
        # Copy model file
        import shutil
        shutil.copy2(source_path, target_path)
        
        return target_name
    
    def remove_pretrained_model(self, model_name: str) -> bool:
        """
        Remove a pretrained model.
        
        Args:
            model_name: Name of the model to remove
            
        Returns:
            True if model was removed, False if not found
        """
        model_path = self.pretrain_dir / model_name
        if model_path.exists():
            model_path.unlink()
            return True
        return False
    
    def get_pretrained_model_path(self, model_name: str) -> Optional[Path]:
        """Get absolute path to pretrained model."""
        model_path = self.pretrain_dir / model_name
        return model_path if model_path.exists() else None
    
    def get_trained_model_path(self, model_name: str) -> Optional[Path]:
        """Get absolute path to trained model."""
        model_path = self.model_dir / model_name
        return model_path if model_path.exists() else None
    
    def create_training_plan(self, name: str, pretrained_model: Optional[str] = None) -> PlanContext:
        """Create a new training plan."""
        return self.plan_manager.create_plan(name, pretrained_model)
    
    def get_training_plan(self, plan_id: str) -> Optional[PlanContext]:
        """Get training plan by ID."""
        return self.plan_manager.get_plan(plan_id)
    
    def get_all_training_plans(self) -> List[PlanContext]:
        """Get all training plans."""
        return self.plan_manager.get_all_plans()
    
    def delete_training_plan(self, plan_id: str) -> bool:
        """Delete a training plan."""
        return self.plan_manager.delete_plan(plan_id)
    
    def get_model_summary(self) -> Dict[str, Any]:
        """
        Get summary of all models and plans.
        
        Returns:
            Dictionary with model counts and information
        """
        return {
            "pretrained_models": len(self.get_pretrained_models()),
            "trained_models": len(self.get_trained_models()),
            "training_plans": self.plan_manager.get_plan_count(),
            "completed_plans": len(self.plan_manager.get_plans_by_status(True)),
            "pending_plans": len(self.plan_manager.get_plans_by_status(False))
        }
    
    def __str__(self) -> str:
        summary = self.get_model_summary()
        return f"ProjectModelManager({summary['pretrained_models']} pretrained, {summary['training_plans']} plans)"
    
    def __repr__(self) -> str:
        return self.__str__()
