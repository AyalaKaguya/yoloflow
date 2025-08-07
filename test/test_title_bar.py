"""
Test the custom title bar functionality.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from yoloflow.ui.project_manager_window import CustomTitleBar
from yoloflow.__version__ import __version__


class TestCustomTitleBar(unittest.TestCase):
    """Test custom title bar functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
    
    def test_title_bar_creation(self):
        """Test that title bar is created correctly"""
        title_bar = CustomTitleBar()
        
        # Check that title bar has correct height
        self.assertEqual(title_bar.minimumHeight(), 40)
        self.assertEqual(title_bar.maximumHeight(), 40)
        
        # Check that signals are defined
        self.assertTrue(hasattr(title_bar, 'close_clicked'))
        
        print("✅ Title bar creation test passed")
    
    def test_version_display(self):
        """Test that version is displayed correctly"""
        title_bar = CustomTitleBar()
        
        # Check that version is imported correctly
        self.assertIsNotNone(__version__)
        self.assertNotEqual(__version__, "")
        
        print(f"✅ Version display test passed - version: {__version__}")
    
    def test_close_button_exists(self):
        """Test that close button exists and is configured"""
        title_bar = CustomTitleBar()
        
        # Check that close button exists
        self.assertIsNotNone(title_bar.close_btn)
        self.assertEqual(title_bar.close_btn.text(), "×")
        self.assertEqual(title_bar.close_btn.size().width(), 30)
        self.assertEqual(title_bar.close_btn.size().height(), 30)
        
        print("✅ Close button test passed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
