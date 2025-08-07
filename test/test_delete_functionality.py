#!/usr/bin/env python3
"""
测试删除项目功能
"""

import unittest
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from yoloflow.ui.project_manager_window import RecentProjectItem


class TestDeleteFunction(unittest.TestCase):
    """测试删除功能"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
    
    def test_delete_button_exists(self):
        """测试删除按钮存在"""
        project_data = {
            'name': '测试项目',
            'path': '/test/path',
            'last_opened_at': '2025-08-07T15:00:00.000000',
            'task_type': 'detection'
        }
        
        item = RecentProjectItem(project_data)
        
        # 检查删除按钮存在
        self.assertTrue(hasattr(item, 'delete_btn'))
        self.assertIsNotNone(item.delete_btn)
        self.assertEqual(item.delete_btn.text(), "🗑")
        self.assertEqual(item.delete_btn.size().width(), 30)
        self.assertEqual(item.delete_btn.size().height(), 30)
        
        print("✅ 删除按钮存在测试通过")
    
    def test_delete_signal_emitted(self):
        """测试删除信号能够发出"""
        project_data = {
            'name': '测试项目',
            'path': '/test/path',
            'last_opened_at': '2025-08-07T15:00:00.000000',
            'task_type': 'detection'
        }
        
        item = RecentProjectItem(project_data)
        
        # 检查信号存在
        self.assertTrue(hasattr(item, 'delete_requested'))
        
        # 测试信号连接（点击删除按钮会发出信号）
        signal_emitted = False
        received_path = None
        
        def on_delete_requested(path):
            nonlocal signal_emitted, received_path
            signal_emitted = True
            received_path = path
        
        item.delete_requested.connect(on_delete_requested)
        item.delete_btn.click()
        
        self.assertTrue(signal_emitted)
        self.assertEqual(received_path, '/test/path')
        
        print("✅ 删除信号发出测试通过")
    
    def test_layout_structure(self):
        """测试布局结构正确"""
        project_data = {
            'name': '测试项目',
            'path': '/test/path',
            'last_opened_at': '2025-08-07T15:00:00.000000',
            'task_type': 'detection'
        }
        
        item = RecentProjectItem(project_data)
        
        # 检查主布局是水平布局
        main_layout = item.layout()
        self.assertEqual(main_layout.count(), 2)  # 信息布局 + 删除按钮
        
        print("✅ 布局结构测试通过")


if __name__ == "__main__":
    unittest.main(verbosity=2)
