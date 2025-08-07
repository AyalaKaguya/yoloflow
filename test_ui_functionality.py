"""
Test script to verify project manager functionality.
"""

import unittest
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from yoloflow.service.project_manager import ProjectManager
from yoloflow.model import TaskType


class TestProjectManagerUI(unittest.TestCase):
    """Test project manager UI functionality"""
    
    def test_recent_projects_loading(self):
        """Test loading recent projects"""
        manager = ProjectManager()
        
        # Get recent projects
        recent_projects = manager.get_recent_projects(limit=10)
        
        print(f"Found {len(recent_projects)} recent projects:")
        for project in recent_projects:
            print(f"  - {project['name']} ({project['task_type']})")
            print(f"    Path: {project['path']}")
            print(f"    Last opened: {project.get('last_opened_at', 'Never')}")
            print()
        
        manager.close()
        
        # Should have at least the sample projects we created
        self.assertGreaterEqual(len(recent_projects), 3)
    
    def test_project_data_structure(self):
        """Test that project data has required fields"""
        manager = ProjectManager()
        
        recent_projects = manager.get_recent_projects(limit=1)
        
        if recent_projects:
            project = recent_projects[0]
            
            # Check required fields
            required_fields = ['name', 'path', 'task_type', 'created_at']
            for field in required_fields:
                self.assertIn(field, project, f"Missing required field: {field}")
            
            print(f"Project data structure is valid: {list(project.keys())}")
        
        manager.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
