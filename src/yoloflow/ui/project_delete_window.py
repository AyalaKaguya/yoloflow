"""
项目删除确认界面
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QCheckBox, QFrame, QMainWindow
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..service.project_manager import ProjectManager
from .components import CustomTitleBar


class ProjectDeleteWindow(QMainWindow):
    """项目删除确认界面"""
    
    delete_confirmed = Signal(str, bool)  # 删除确认信号 (project_path, delete_files)
    delete_cancelled = Signal()  # 取消删除信号
    
    def __init__(self, project_path: str, project_manager: Optional[ProjectManager] = None):
        super().__init__()
        self.project_path = project_path
        self.project_manager = project_manager or ProjectManager()
        self.project_data = None
        self._load_project_data()
        self._setup_ui()
    
    def _load_project_data(self):
        """加载项目数据"""
        try:
            # 从数据库获取项目信息
            recent_projects = self.project_manager.get_recent_projects(limit=100)
            for project in recent_projects:
                if project['path'] == self.project_path:
                    self.project_data = project
                    break
            
            # 如果数据库中没有，创建基本数据
            if not self.project_data:
                self.project_data = {
                    'name': Path(self.project_path).name,
                    'path': self.project_path,
                    'created_at': 'Unknown',
                    'last_opened_at': 'Unknown',
                    'description': '无描述'
                }
        except Exception as e:
            # 错误时创建默认数据
            self.project_data = {
                'name': Path(self.project_path).name,
                'path': self.project_path,
                'created_at': 'Unknown',
                'last_opened_at': 'Unknown',
                'description': '无描述'
            }
    
    def _setup_ui(self):
        """设置界面"""
        # 设置窗口属性
        self.setWindowTitle("删除项目")
        self.setFixedSize(600, 450)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 主widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 垂直布局包含标题栏和内容区域
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 自定义标题栏
        self.title_bar = CustomTitleBar(self, "YOLOFlow - 删除项目")
        self.title_bar.close_clicked.connect(self.close)
        main_layout.addWidget(self.title_bar)
        
        # 内容区域
        content_widget = self._create_content_area()
        main_layout.addWidget(content_widget)
        
        # 设置整体样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)
    
    def _create_content_area(self):
        """创建内容区域"""
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
            }
        """)
        
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 警告标题
        warning_label = QLabel("⚠️ 删除项目确认")
        warning_font = QFont()
        warning_font.setPointSize(16)
        warning_font.setBold(True)
        warning_label.setFont(warning_font)
        warning_label.setStyleSheet("color: #e74c3c; margin-bottom: 10px;")
        layout.addWidget(warning_label)
        
        # 提示信息
        info_label = QLabel("您确定要删除以下项目吗？此操作无法撤销。")
        info_label.setStyleSheet("color: #ffffff; font-size: 14px; margin-bottom: 20px;")
        layout.addWidget(info_label)
        
        # 项目信息区域
        project_info_frame = self._create_project_info_frame()
        layout.addWidget(project_info_frame)
        
        # 选项区域
        options_frame = self._create_options_frame()
        layout.addWidget(options_frame)
        
        # 按钮区域
        buttons_frame = self._create_buttons_frame()
        layout.addWidget(buttons_frame)
        
        layout.addStretch()
        
        return content_widget
    
    def _create_project_info_frame(self):
        """创建项目信息框架"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #363636;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(12)
        
        # 项目名称
        name_label = QLabel(f"项目名称: {self.project_data['name']}")
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(name_label)
        
        # 项目路径
        path_label = QLabel(f"项目路径: {self.project_data['path']}")
        path_label.setStyleSheet("color: #b0b0b0; font-size: 11px;")
        path_label.setWordWrap(True)
        layout.addWidget(path_label)
        
        # 创建时间
        if self.project_data.get('created_at') and self.project_data['created_at'] != 'Unknown':
            try:
                created_time = datetime.fromisoformat(self.project_data['created_at'])
                created_str = created_time.strftime("%Y-%m-%d %H:%M")
            except:
                created_str = self.project_data['created_at']
        else:
            created_str = "未知"
        
        created_label = QLabel(f"创建时间: {created_str}")
        created_label.setStyleSheet("color: #b0b0b0; font-size: 11px;")
        layout.addWidget(created_label)
        
        # 最后打开时间
        if self.project_data.get('last_opened_at') and self.project_data['last_opened_at'] != 'Unknown':
            try:
                last_opened = datetime.fromisoformat(self.project_data['last_opened_at'])
                last_opened_str = last_opened.strftime("%Y-%m-%d %H:%M")
            except:
                last_opened_str = self.project_data['last_opened_at']
        else:
            last_opened_str = "从未打开"
        
        last_opened_label = QLabel(f"最后打开: {last_opened_str}")
        last_opened_label.setStyleSheet("color: #b0b0b0; font-size: 11px;")
        layout.addWidget(last_opened_label)
        
        # 描述
        description = self.project_data.get('description', '无描述')
        desc_label = QLabel(f"描述: {description}")
        desc_label.setStyleSheet("color: #b0b0b0; font-size: 11px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        return frame
    
    def _create_options_frame(self):
        """创建选项框架"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #363636;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # 删除文件夹选项
        self.delete_files_checkbox = QCheckBox("同时删除项目文件夹")
        self.delete_files_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #404040;
                border: 2px solid #808080;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #e74c3c;
                border: 2px solid #e74c3c;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(self.delete_files_checkbox)
        
        # 警告文字
        warning_text = QLabel("⚠️ 如果选择删除文件夹，所有项目文件将被永久删除且无法恢复！")
        warning_text.setStyleSheet("color: #e67e22; font-size: 10px; margin-top: 8px;")
        warning_text.setWordWrap(True)
        layout.addWidget(warning_text)
        
        return frame
    
    def _create_buttons_frame(self):
        """创建按钮框架"""
        frame = QFrame()
        
        layout = QHBoxLayout(frame)
        layout.setSpacing(15)
        
        # 弹性空间
        layout.addStretch()
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #494f54;
            }
        """)
        cancel_btn.clicked.connect(self._on_cancel)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(cancel_btn)
        
        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setFixedSize(100, 40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        delete_btn.clicked.connect(self._on_delete)
        delete_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(delete_btn)
        
        return frame
    
    def _on_cancel(self):
        """取消删除"""
        self.delete_cancelled.emit()
        self.close()
    
    def _on_delete(self):
        """确认删除"""
        delete_files = self.delete_files_checkbox.isChecked()
        self.delete_confirmed.emit(self.project_path, delete_files)
        self.close()
    
    def closeEvent(self, event):
        """关闭事件"""
        event.accept()
