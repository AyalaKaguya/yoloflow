"""
Project Manager Main Window.

项目管理器主界面，用于创建新项目、打开已有项目和管理最近项目。
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, 
    QListWidgetItem, QLabel, QFrame, QFileDialog, QMessageBox,
    QApplication, QMainWindow
)
from PySide6.QtCore import Qt, QSize, Signal, QPoint
from PySide6.QtGui import QFont, QPalette, QColor, QMouseEvent

from ..service.project_manager import ProjectManager
from ..model import TaskType
from ..__version__ import __version__


class CustomTitleBar(QWidget):
    """自定义标题栏"""
    
    close_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.dragging = False
        self.drag_position = QPoint()
        self._setup_ui()
    
    def _setup_ui(self):
        """设置标题栏UI"""
        self.setFixedHeight(40)
        self.setStyleSheet("""
            CustomTitleBar {
                background-color: #2c3e50;
                border-bottom: 1px solid #34495e;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 10, 0)
        layout.setSpacing(10)
        
        # 应用名称和版本号
        title_label = QLabel(f"YOLOFlow v{__version__}")
        title_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # 弹性空间
        layout.addStretch()
        
        # 关闭按钮
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #bdc3c7;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        self.close_btn.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self.close_btn)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件 - 开始拖拽"""
        if event.button() == Qt.LeftButton and self.parent_window:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件 - 拖拽窗口"""
        if event.buttons() == Qt.LeftButton and self.dragging and self.parent_window:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件 - 结束拖拽"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()


class RecentProjectItem(QWidget):
    """最近项目列表项的自定义widget"""
    
    project_clicked = Signal(str)  # 项目路径信号
    
    def __init__(self, project_data: Dict[str, Any]):
        super().__init__()
        self.project_path = project_data['path']
        self._setup_ui(project_data)
    
    def _setup_ui(self, project_data: Dict[str, Any]):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        
        # 项目名称
        name_label = QLabel(project_data['name'])
        name_font = QFont()
        name_font.setPointSize(11)
        name_font.setBold(True)
        name_label.setFont(name_font)
        layout.addWidget(name_label)
        
        # 项目路径
        path_label = QLabel(project_data['path'])
        path_label.setStyleSheet("color: #666666;")
        path_font = QFont()
        path_font.setPointSize(9)
        path_label.setFont(path_font)
        layout.addWidget(path_label)
        
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
        time_label.setStyleSheet("color: #888888;")
        time_font = QFont()
        time_font.setPointSize(8)
        time_label.setFont(time_font)
        layout.addWidget(time_label)
        
        # 设置样式
        self.setStyleSheet("""
            RecentProjectItem {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }
            RecentProjectItem:hover {
                background-color: #e8f4f8;
                border-color: #4a9eff;
            }
        """)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.project_clicked.emit(self.project_path)
        super().mousePressEvent(event)


class ProjectManagerWindow(QMainWindow):
    """项目管理器主界面"""
    
    def __init__(self):
        super().__init__()
        self.project_manager = ProjectManager()
        self._setup_ui()
        self._load_recent_projects()
    
    def _setup_ui(self):
        """设置界面"""
        # 设置窗口属性
        self.setWindowTitle("YOLOFlow - 项目管理器")
        self.setFixedSize(900, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        
        # 主widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 垂直布局包含标题栏和内容区域
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 自定义标题栏
        self.title_bar = CustomTitleBar(self)
        self.title_bar.close_clicked.connect(self.close)
        main_layout.addWidget(self.title_bar)
        
        # 内容区域布局
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 左侧面板
        left_panel = self._create_left_panel()
        content_layout.addWidget(left_panel)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #d0d0d0;")
        content_layout.addWidget(separator)
        
        # 右侧面板
        right_panel = self._create_right_panel()
        content_layout.addWidget(right_panel)
        
        # 设置比例
        content_layout.setStretch(0, 1)  # 左侧面板
        content_layout.setStretch(2, 2)  # 右侧面板
        
        # 将内容布局添加到主布局
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        
        # 设置整体样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
    
    def _create_left_panel(self):
        """创建左侧按钮面板"""
        panel = QWidget()
        panel.setFixedWidth(300)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(20)
        
        # 创建新项目按钮
        self.btn_new_project = QPushButton("创建新项目")
        self.btn_new_project.setFixedHeight(50)
        self.btn_new_project.clicked.connect(self._create_new_project)
        layout.addWidget(self.btn_new_project)
        
        # 打开已有项目按钮
        self.btn_open_project = QPushButton("打开已有项目")
        self.btn_open_project.setFixedHeight(50)
        self.btn_open_project.clicked.connect(self._open_existing_project)
        layout.addWidget(self.btn_open_project)
        
        # 设置按钮
        self.btn_settings = QPushButton("设置")
        self.btn_settings.setFixedHeight(50)
        self.btn_settings.clicked.connect(self._open_settings)
        layout.addWidget(self.btn_settings)
        
        # 弹性空间
        layout.addStretch()
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f5f8b;
            }
        """
        
        self.btn_new_project.setStyleSheet(button_style)
        self.btn_open_project.setStyleSheet(button_style)
        self.btn_settings.setStyleSheet(button_style.replace("#3498db", "#95a5a6").replace("#2980b9", "#7f8c8d").replace("#1f5f8b", "#6c7b7d"))
        
        return panel
    
    def _create_right_panel(self):
        """创建右侧项目列表面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("最近项目")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 项目列表
        self.recent_projects_list = QListWidget()
        self.recent_projects_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #fafafa;
            }
            QListWidget::item {
                border: none;
                padding: 5px;
                margin: 3px;
            }
        """)
        layout.addWidget(self.recent_projects_list)
        
        return panel
    
    def _load_recent_projects(self):
        """加载最近项目列表"""
        self.recent_projects_list.clear()
        
        try:
            recent_projects = self.project_manager.get_recent_projects(limit=10)
            
            if not recent_projects:
                # 显示空状态
                item = QListWidgetItem()
                empty_widget = QLabel("暂无最近项目\n点击左侧按钮创建或打开项目")
                empty_widget.setAlignment(Qt.AlignCenter)
                empty_widget.setStyleSheet("color: #888888; padding: 40px;")
                item.setSizeHint(empty_widget.sizeHint())
                self.recent_projects_list.addItem(item)
                self.recent_projects_list.setItemWidget(item, empty_widget)
                return
            
            for project_data in recent_projects:
                self._add_project_item(project_data)
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载最近项目失败: {str(e)}")
    
    def _add_project_item(self, project_data: Dict[str, Any]):
        """添加项目项到列表"""
        item = QListWidgetItem()
        project_widget = RecentProjectItem(project_data)
        project_widget.project_clicked.connect(self._open_project_from_list)
        
        item.setSizeHint(QSize(0, 80))  # 设置项目高度
        self.recent_projects_list.addItem(item)
        self.recent_projects_list.setItemWidget(item, project_widget)
    
    def _create_new_project(self):
        """创建新项目"""
        # TODO: 这里之后会打开创建新项目的对话框
        QMessageBox.information(self, "提示", "创建新项目功能将在下一步实现")
    
    def _open_existing_project(self):
        """打开已有项目"""
        project_dir = QFileDialog.getExistingDirectory(
            self, 
            "选择项目文件夹",
            str(Path.home())
        )
        
        if project_dir:
            try:
                # 尝试打开项目
                project = self.project_manager.open_project(project_dir)
                QMessageBox.information(self, "成功", f"已打开项目: {project.name}")
                self._load_recent_projects()  # 刷新最近项目列表
                
                # TODO: 这里之后会打开项目主界面
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开项目失败: {str(e)}")
    
    def _open_settings(self):
        """打开设置"""
        # TODO: 这里之后会打开设置对话框
        QMessageBox.information(self, "提示", "设置功能将在后续实现")
    
    def _open_project_from_list(self, project_path: str):
        """从列表中打开项目"""
        try:
            project = self.project_manager.open_project(project_path)
            QMessageBox.information(self, "成功", f"已打开项目: {project.name}")
            self._load_recent_projects()  # 刷新最近项目列表
            
            # TODO: 这里之后会打开项目主界面
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开项目失败: {str(e)}")
    
    def closeEvent(self, event):
        """关闭事件"""
        self.project_manager.close()
        event.accept()


def show_project_manager():
    """显示项目管理器界面的便利函数"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = ProjectManagerWindow()
    window.show()
    
    return app, window


if __name__ == "__main__":
    app, window = show_project_manager()
    sys.exit(app.exec())
