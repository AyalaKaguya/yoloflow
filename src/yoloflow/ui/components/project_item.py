"""
项目列表项组件
"""

from datetime import datetime
from typing import Dict, Any

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class RecentProjectItem(QWidget):
    """最近项目列表项的自定义widget"""
    
    project_clicked = Signal(str)  # 项目路径信号
    delete_requested = Signal(str)  # 删除项目信号
    
    def __init__(self, project_data: Dict[str, Any]):
        super().__init__()
        self.project_path = project_data['path']
        self.is_hovered = False
        self._setup_ui(project_data)
        # 启用鼠标追踪来接收鼠标进入/离开事件
        self.setMouseTracking(True)
    
    def _setup_ui(self, project_data: Dict[str, Any]):
        """设置UI"""
        # 主布局 - 水平布局包含项目信息和删除按钮
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(10)
        
        # 项目信息布局 - 垂直布局
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # 项目名称
        name_label = QLabel(project_data['name'])
        name_font = QFont()
        name_font.setPointSize(11)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #ffffff; background: transparent; line-height: 1.4;")
        name_label.setWordWrap(True)
        name_label.setMinimumHeight(24)
        info_layout.addWidget(name_label)
        
        # 添加项目名称与下面内容的间距
        info_layout.addSpacing(6)
        
        # 项目路径
        path_label = QLabel(project_data['path'])
        path_label.setStyleSheet("color: #b0b0b0; background: transparent;")
        path_font = QFont()
        path_font.setPointSize(9)
        path_label.setFont(path_font)
        info_layout.addWidget(path_label)
        
        # 最后打开时间
        if project_data.get('last_opened_at'):
            try:
                # 解析ISO格式时间
                last_opened = datetime.fromisoformat(project_data['last_opened_at'])
                time_str = last_opened.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = project_data['last_opened_at']
        else:
            time_str = "从未打开"
            
        time_label = QLabel(f"最后打开: {time_str}")
        time_label.setStyleSheet("color: #808080; background: transparent;")
        time_font = QFont()
        time_font.setPointSize(8)
        time_label.setFont(time_font)
        info_layout.addWidget(time_label)
        
        # 将项目信息布局添加到主布局
        main_layout.addLayout(info_layout)
        
        # 删除按钮
        self.delete_btn = QPushButton("🗑")
        self.delete_btn.setFixedSize(30, 30)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #808080;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        self.delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.project_path))
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        main_layout.addWidget(self.delete_btn)
        
        # 设置初始样式
        self._update_style()
    
    def _update_style(self):
        """更新样式"""
        if self.is_hovered:
            self.setStyleSheet("""
                RecentProjectItem {
                    background-color: #4a4a4a;
                    border: 1px solid #4a90e2;
                    border-radius: 6px;
                }
            """)
        else:
            self.setStyleSheet("""
                RecentProjectItem {
                    background-color: #404040;
                    border: 1px solid #5a5a5a;
                    border-radius: 6px;
                }
            """)
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self.is_hovered = True
        self._update_style()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.is_hovered = False
        self._update_style()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.project_clicked.emit(self.project_path)
        super().mousePressEvent(event)
