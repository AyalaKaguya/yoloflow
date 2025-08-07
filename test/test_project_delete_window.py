#!/usr/bin/env python3
"""
测试项目删除界面功能
"""

import unittest
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from yoloflow.ui.project_delete_window import ProjectDeleteWindow


class TestProjectDeleteWindow(unittest.TestCase):
    """测试项目删除界面"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
    
    def test_delete_window_creation(self):
        """测试删除窗口创建"""
        test_path = "/test/project/path"
        window = ProjectDeleteWindow(test_path)
        
        # 检查窗口属性
        self.assertEqual(window.project_path, test_path)
        self.assertIsNotNone(window.project_data)
        self.assertEqual(window.windowTitle(), "删除项目")
        
        # 检查窗口大小
        self.assertEqual(window.size().width(), 600)
        self.assertEqual(window.size().height(), 450)
        
        # 检查无边框
        self.assertTrue(window.windowFlags() & Qt.FramelessWindowHint)
        
        print("✅ 删除窗口创建测试通过")
    
    def test_title_bar_exists(self):
        """测试标题栏存在"""
        test_path = "/test/project/path"
        window = ProjectDeleteWindow(test_path)
        
        # 检查标题栏存在
        self.assertTrue(hasattr(window, 'title_bar'))
        self.assertIsNotNone(window.title_bar)
        
        print("✅ 标题栏存在测试通过")
    
    def test_delete_files_checkbox(self):
        """测试删除文件选项框"""
        test_path = "/test/project/path"
        window = ProjectDeleteWindow(test_path)
        
        # 检查选项框存在
        self.assertTrue(hasattr(window, 'delete_files_checkbox'))
        self.assertIsNotNone(window.delete_files_checkbox)
        
        # 检查初始状态
        self.assertFalse(window.delete_files_checkbox.isChecked())
        
        # 测试选中状态
        window.delete_files_checkbox.setChecked(True)
        self.assertTrue(window.delete_files_checkbox.isChecked())
        
        print("✅ 删除文件选项框测试通过")
    
    def test_signals_exist(self):
        """测试信号存在"""
        test_path = "/test/project/path"
        window = ProjectDeleteWindow(test_path)
        
        # 检查信号存在
        self.assertTrue(hasattr(window, 'delete_confirmed'))
        self.assertTrue(hasattr(window, 'delete_cancelled'))
        
        print("✅ 信号存在测试通过")
    
    def test_project_data_loading(self):
        """测试项目数据加载"""
        test_path = "/test/project/path"
        window = ProjectDeleteWindow(test_path)
        
        # 检查项目数据结构
        self.assertIsInstance(window.project_data, dict)
        self.assertIn('name', window.project_data)
        self.assertIn('path', window.project_data)
        self.assertIn('created_at', window.project_data)
        self.assertIn('last_opened_at', window.project_data)
        
        # 检查路径正确
        self.assertEqual(window.project_data['path'], test_path)
        
        print("✅ 项目数据加载测试通过")


if __name__ == "__main__":
    unittest.main(verbosity=2)
