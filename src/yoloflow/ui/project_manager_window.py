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

from ..service import ProjectManager
from ..__version__ import __version__
from .components import CustomTitleBar, RecentProjectItem
from .project_delete_window import ProjectDeleteWindow
from .create_project_wizard import CreateProjectWizard
from .workspace_window import WorkspaceWindow


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
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)  # 无边框

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
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
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
        self.btn_new_project.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_project.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)

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
        title_label.setStyleSheet(
            "color: #ffffff; margin-bottom: 10px; margin-top: 10px;")
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
            recent_projects = self.project_manager.get_recent_projects(
                limit=10)

            if not recent_projects:
                # 显示空状态
                item = QListWidgetItem()
                empty_widget = QLabel("暂无最近项目\n点击左侧按钮创建或打开项目")
                empty_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                empty_widget.setStyleSheet(
                    "color: #808080; padding: 40px; font-size: 14px; background: transparent;")
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
        # 创建独立的向导窗口，不设置父窗口以确保完全独立
        self.wizard = CreateProjectWizard()
        self.wizard.project_created.connect(self._on_project_created)
        self.wizard.show()  # 显示独立窗口

    def _on_project_created(self, project_dir: str):
        """项目创建完成后的处理"""
        try:
            # 尝试打开项目
            project = self.project_manager.open_project(project_dir)
            self._load_recent_projects()  # 刷新最近项目列表

            # 打开工作区窗口
            self._open_workspace(project)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理新创建的项目时发生错误：{str(e)}")

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
                self._load_recent_projects()  # 刷新最近项目列表

                # 打开工作区窗口
                self._open_workspace(project)

            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开项目失败: {str(e)}")

    def _open_settings(self):
        """打开设置"""
        # TODO: 这里之后会打开设置对话框
        QMessageBox.information(self, "提示", "设置功能将在后续实现")

    def _delete_project(self, project_path: str):
        """删除项目 - 打开删除确认界面"""
        delete_window = ProjectDeleteWindow(project_path, self.project_manager)
        delete_window.delete_confirmed.connect(self._on_delete_confirmed)
        delete_window.delete_cancelled.connect(self._on_delete_cancelled)
        delete_window.show()

    def _on_delete_confirmed(self, project_path: str, delete_files: bool):
        """删除确认后的处理"""
        try:
            self.project_manager.remove_project(
                project_path, delete_files=delete_files)
            # 刷新项目列表
            self._load_recent_projects()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除项目失败: {str(e)}")

    def _on_delete_cancelled(self):
        """删除取消后的处理"""
        pass  # 不需要特殊处理

    def _open_project_from_list(self, project_path: str):
        """从列表中打开项目"""
        try:
            project = self.project_manager.open_project(project_path)
            self._load_recent_projects()  # 刷新最近项目列表

            # 打开工作区窗口
            self._open_workspace(project)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开项目失败: {str(e)}")
    
    def _open_workspace(self, project):
        """打开工作区窗口"""
        # 创建工作区窗口
        self.workspace_window = WorkspaceWindow(project, self.project_manager, None)
        self.workspace_window.closed.connect(self._on_workspace_closed)
        self.workspace_window.show()
        
        # 关闭项目管理器
        self.close()
    
    def _on_workspace_closed(self):
        """工作区窗口关闭时的处理"""
        # 工作区关闭时，重新显示项目管理器
        # 注意：如果用户选择退出应用，这个方法不会被调用，因为整个应用都会退出
        self.show()

    def closeEvent(self, event):
        """关闭事件"""
        self.project_manager.close()
        event.accept()


