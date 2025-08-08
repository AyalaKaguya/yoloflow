"""
Manager for training plans within a project.
"""

from pathlib import Path
from typing import Dict, List, Optional

from ..enums import TaskType
from .plan_context import PlanContext
from .project_config import ProjectConfig


class ProjectPlanManager:
    """
    Manager for training plans within a project.
    
    Handles creation, loading, and management of training plans.
    """
    
    def __init__(self, project_path: Path, project_config: ProjectConfig):
        """
        Initialize plan manager.
        
        Args:
            project_path: Path to the project directory
            project_config: Project configuration instance
        """
        self.project_path = Path(project_path)
        self.config = project_config
        self.task_type = project_config.task_type
        self.model_dir = self.project_path / "model"
        
        # Ensure model directory exists
        self.model_dir.mkdir(exist_ok=True)
        
        # Cache for loaded plans
        self._plans_cache: Dict[str, PlanContext] = {}
        self._load_all_plans()
    
    def _load_all_plans(self):
        """Load all existing plans from model directory."""
        if not self.model_dir.exists():
            return
        
        for plan_file in self.model_dir.glob("*.toml"):
            try:
                plan = PlanContext.load_from_file(plan_file)
                self._plans_cache[plan.plan_id] = plan
            except Exception as e:
                print(f"Warning: Failed to load plan {plan_file}: {e}")
    
    def create_plan(
        self,
        name: str,
        pretrained_model: Optional[str] = None
    ) -> PlanContext:
        """
        Create a new training plan.
        
        Args:
            name: User-defined plan name
            pretrained_model: Path to pretrained model (relative to project)
            
        Returns:
            Created PlanContext instance
            
        Raises:
            ValueError: If plan name already exists
        """
        # Check for duplicate names
        for plan in self._plans_cache.values():
            if plan.name == name:
                raise ValueError(f"Plan with name '{name}' already exists")
        
        # Create new plan
        plan = PlanContext.create_new(name, self.project_path, self.task_type, pretrained_model)
        
        # Save and cache
        plan.save()
        self._plans_cache[plan.plan_id] = plan
        
        return plan
    
    def get_plan(self, plan_id: str) -> Optional[PlanContext]:
        """Get plan by ID."""
        return self._plans_cache.get(plan_id)
    
    def get_plan_by_name(self, name: str) -> Optional[PlanContext]:
        """Get plan by name."""
        for plan in self._plans_cache.values():
            if plan.name == name:
                return plan
        return None
    
    def get_all_plans(self) -> List[PlanContext]:
        """Get all plans ordered by creation time."""
        plans = list(self._plans_cache.values())
        return sorted(plans, key=lambda p: p.created_at, reverse=True)
    
    def delete_plan(self, plan_id: str) -> bool:
        """
        Delete a training plan.
        
        Args:
            plan_id: Plan ID to delete
            
        Returns:
            True if plan was deleted, False if not found
        """
        plan = self._plans_cache.get(plan_id)
        if plan:
            plan.delete()
            del self._plans_cache[plan_id]
            return True
        return False
    
    def update_plan(self, plan_id: str) -> bool:
        """
        Update a plan in cache and save to file.
        
        Args:
            plan_id: Plan ID to update
            
        Returns:
            True if plan was updated, False if not found
        """
        plan = self._plans_cache.get(plan_id)
        if plan:
            plan.save()
            return True
        return False
    
    def get_plans_by_status(self, has_results: bool) -> List[PlanContext]:
        """Get plans by result status."""
        return [plan for plan in self._plans_cache.values() 
                if plan.has_results() == has_results]
    
    def get_plan_count(self) -> int:
        """Get total number of plans."""
        return len(self._plans_cache)
    
    def search_plans(self, query: str) -> List[PlanContext]:
        """Search plans by name."""
        query = query.lower()
        return [plan for plan in self._plans_cache.values() 
                if query in plan.name.lower()]
    
    def __str__(self) -> str:
        return f"ProjectPlanManager({self.get_plan_count()} plans)"
    
    def __repr__(self) -> str:
        return self.__str__()
