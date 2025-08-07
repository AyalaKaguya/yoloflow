#!/usr/bin/env python3
"""
测试列表项样式优化
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from src.yoloflow.ui.project_manager_window import RecentProjectItem

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("列表项样式测试")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #2b2b2b;")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 创建测试项目数据
        test_projects = [
            {
                'name': '测试项目 1',
                'path': '/path/to/test/project1',
                'last_opened_at': '2025-08-07T15:00:00.000000',
                'task_type': 'detection'
            },
            {
                'name': '长名称的测试项目',
                'path': '/very/long/path/to/another/test/project/with/very/long/name',
                'last_opened_at': '2025-08-06T10:30:00.000000',
                'task_type': 'classification'
            },
            {
                'name': '最新项目',
                'path': '/recent/project',
                'last_opened_at': '2025-08-07T16:45:00.000000',
                'task_type': 'segmentation'
            }
        ]
        
        # 添加测试项目
        for project_data in test_projects:
            item = RecentProjectItem(project_data)
            layout.addWidget(item)
        
        layout.addStretch()

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("测试列表项样式:")
    print("- ✅ 缩小了内边距 (从15,12减少到12,10)")
    print("- ✅ 为所有文字标签添加了 background: transparent")
    print("- ✅ 增加了项目名称与下面内容的间距 (addSpacing(6))")
    print("- ✅ 减小了整体元素间距 (从4减少到2)")
    print("\n移动鼠标到项目上查看悬停效果...")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
