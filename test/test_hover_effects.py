"""
Test the hover effects and dark theme functionality.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QEvent, QPointF
from PySide6.QtGui import QEnterEvent
from yoloflow.ui.project_manager_window import RecentProjectItem


class TestHoverEffects(unittest.TestCase):
    """Test hover effects in project manager"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
    
    def test_project_item_creation(self):
        """Test that project item is created with dark theme"""
        project_data = {
            'name': 'Test Project',
            'path': '/test/path',
            'last_opened_at': '2025-08-07T15:00:00.000000',
            'task_type': 'detection'
        }
        
        item = RecentProjectItem(project_data)
        
        # Check that item has tracking enabled
        self.assertTrue(item.hasMouseTracking())
        
        # Check initial state
        self.assertFalse(item.is_hovered)
        
        print("✅ Project item creation test passed")
    
    def test_hover_state_changes(self):
        """Test that hover state changes correctly"""
        project_data = {
            'name': 'Test Project',
            'path': '/test/path',
            'last_opened_at': '2025-08-07T15:00:00.000000',
            'task_type': 'detection'
        }
        
        item = RecentProjectItem(project_data)
        
        # Simulate mouse enter
        enter_event = QEnterEvent(QPointF(10, 10), QPointF(10, 10), QPointF(10, 10))
        item.enterEvent(enter_event)
        self.assertTrue(item.is_hovered)

        # Simulate mouse leave
        leave_event = QEvent(QEvent.Leave)
        item.leaveEvent(leave_event)
        self.assertFalse(item.is_hovered)
        
        print("✅ Hover state changes test passed")
    
    def test_dark_theme_colors(self):
        """Test that dark theme colors are applied"""
        project_data = {
            'name': 'Test Project',
            'path': '/test/path',
            'last_opened_at': '2025-08-07T15:00:00.000000',
            'task_type': 'detection'
        }
        
        item = RecentProjectItem(project_data)
        
        # Check that the widget has style applied
        style = item.styleSheet()
        self.assertIn("#404040", style)  # Default background color
        
        print("✅ Dark theme colors test passed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
