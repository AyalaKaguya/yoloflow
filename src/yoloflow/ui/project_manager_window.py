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
        self.close_btn.setFixedSize(40, 30)  # 4:3比例，从30x30改为40x30
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #bdc3c7;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 4px;
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
        self.close_btn.setCursor(Qt.PointingHandCursor)  # 设置鼠标指针为手型
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
        info_layout.setSpacing(4)
        
        # 项目名称
        name_label = QLabel(project_data['name'])
        name_font = QFont()
        name_font.setPointSize(11)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #ffffff; background: transparent;")
        name_label.setWordWrap(True)  # 允许文字换行
        name_label.setMinimumHeight(24)  # 设置最小高度确保显示完整
        info_layout.addWidget(name_label)
        
        # 添加项目名称与下面内容的间距
        info_layout.addSpacing(6)
        
        # 项目路径
        path_label = QLabel(project_data['path'])
        path_label.setStyleSheet("color: #b0b0b0; background: transparent;")  # 确保背景透明
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
        time_label.setStyleSheet("color: #808080; background: transparent;")  # 确保背景透明
        time_font = QFont()
        time_font.setPointSize(8)
        time_label.setFont(time_font)
        info_layout.addWidget(time_label)
        
        # 将项目信息布局添加到主布局
        main_layout.addLayout(info_layout)
        
        # 删除按钮
        self.delete_btn = QPushButton("🗑")  # 使用垃圾桶图标
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
        self.delete_btn.setCursor(Qt.PointingHandCursor)  # 设置鼠标指针为手型
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
        
        # 设置比例 - 调整比例以适应更窄的左栏
        content_layout.setStretch(0, 0)  # 左侧面板固定宽度
        content_layout.setStretch(2, 1)  # 右侧面板占据剩余空间
        
        # 将内容布局添加到主布局
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget)
        
        # 设置整体样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)
    
    def _create_left_panel(self):
        """创建左侧按钮面板"""
        panel = QWidget()
        panel.setFixedWidth(220)  # 从300压缩到220
        panel.setStyleSheet("""
            QWidget {
                background-color: #363636;
                border-right: 1px solid #4a4a4a;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 25, 15, 25)  # 减少边距
        layout.setSpacing(15)  # 减少间距
        
        # 创建新项目按钮
        self.btn_new_project = QPushButton("创建新项目")
        self.btn_new_project.setFixedHeight(40)  # 从50减少到40
        self.btn_new_project.clicked.connect(self._create_new_project)
        layout.addWidget(self.btn_new_project)
        
        # 打开已有项目按钮
        self.btn_open_project = QPushButton("打开已有项目")
        self.btn_open_project.setFixedHeight(40)  # 从50减少到40
        self.btn_open_project.clicked.connect(self._open_existing_project)
        layout.addWidget(self.btn_open_project)
        
        # 设置按钮
        self.btn_settings = QPushButton("设置")
        self.btn_settings.setFixedHeight(40)  # 从50减少到40
        self.btn_settings.clicked.connect(self._open_settings)
        layout.addWidget(self.btn_settings)
        
        # 弹性空间
        layout.addStretch()
        
        # 设置按钮样式 - 深色主题
        button_style = """
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2d5f8f;
            }
        """
        
        settings_style = """
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
        """
        
        self.btn_new_project.setStyleSheet(button_style)
        self.btn_open_project.setStyleSheet(button_style)
        self.btn_settings.setStyleSheet(settings_style)
        
        # 设置鼠标指针为手型
        from PySide6.QtCore import Qt
        self.btn_new_project.setCursor(Qt.PointingHandCursor)
        self.btn_open_project.setCursor(Qt.PointingHandCursor)
        self.btn_settings.setCursor(Qt.PointingHandCursor)
        
        return panel
    
    def _create_right_panel(self):
        """创建右侧项目列表面板"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #202020;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("最近项目")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # 项目列表
        self.recent_projects_list = QListWidget()
        self.recent_projects_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                background-color: #363636;
                outline: none;
            }
            QListWidget::item {
                border: none;
                border-radius: 8px;
                background-color: transparent;
            }
            QListWidget::item:selected {
                background-color: #5a6268;
            }
            QListWidget::item:hover {
                background-color: #5a6268;
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
                empty_widget.setStyleSheet("color: #808080; padding: 40px; font-size: 14px;")
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
        project_widget.delete_requested.connect(self._delete_project)  # 连接删除信号
        
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
    
    def _delete_project(self, project_path: str):
        """删除项目"""
        # 显示确认对话框
        reply = QMessageBox.question(
            self,
            "删除项目",
            f"确定要删除项目记录吗？\n\n项目路径: {project_path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 询问是否删除项目文件夹
                delete_folder_reply = QMessageBox.question(
                    self,
                    "删除项目文件夹",
                    f"是否同时删除项目文件夹？\n\n文件夹: {project_path}\n\n警告：此操作不可恢复！",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                # 根据用户选择删除项目
                delete_files = delete_folder_reply == QMessageBox.Yes
                self.project_manager.remove_project(project_path, delete_files=delete_files)
                
                if delete_files:
                    QMessageBox.information(self, "成功", "项目记录和文件夹已删除")
                else:
                    QMessageBox.information(self, "成功", "项目记录已删除")
                
                # 刷新项目列表
                self._load_recent_projects()
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除项目失败: {str(e)}")
    
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
