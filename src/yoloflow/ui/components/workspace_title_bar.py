"""
工作区标题栏组件
三段式布局：菜单栏 | 项目标题 | 窗口控制
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel,
                               QMenuBar, QMenu, QSizePolicy, QApplication)
from PySide6.QtCore import QByteArray, Qt, Signal, QPoint
from PySide6.QtGui import QMouseEvent, QFontMetrics
from ...__version__ import __version__


class WorkspaceMenuBar(QMenuBar):
    """工作区菜单栏"""

    # 菜单项信号
    new_project = Signal()
    open_project = Signal()
    project_manager = Signal()
    save_project = Signal()
    save_as_project = Signal()
    exit_app = Signal()

    run_current = Signal()
    pause_run = Signal()
    terminate_run = Signal()
    goto_job_page = Signal()

    goto_home = Signal()
    goto_dataset = Signal()
    goto_model = Signal()
    goto_job = Signal()
    goto_training = Signal()
    goto_log = Signal()
    goto_evaluation = Signal()
    goto_export = Signal()

    show_help = Signal()
    show_about = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_menus()
        self.setStyleSheet("""
            QMenuBar {
                background-color: transparent;
                color: #ecf0f1;
                border: none;
                font-size: 12px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
                margin: 0px;
            }
            QMenuBar::item:selected {
                background-color: #34495e;
                border-radius: 3px;
            }
            QMenu {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #34495e;
            }
            QMenu::separator {
                height: 1px;
                background-color: #34495e;
                margin: 3px 10px;
            }
        """)

    def _setup_menus(self):
        """设置菜单"""
        # 项目菜单
        project_menu = self.addMenu("项目")
        project_menu.addAction("新建项目").triggered.connect(self.new_project.emit)
        project_menu.addAction("打开项目").triggered.connect(
            self.open_project.emit)
        project_menu.addAction("项目管理器").triggered.connect(
            self.project_manager.emit)
        project_menu.addSeparator()
        project_menu.addAction("保存").triggered.connect(self.save_project.emit)
        project_menu.addAction("另存为").triggered.connect(
            self.save_as_project.emit)
        project_menu.addSeparator()
        project_menu.addAction("退出").triggered.connect(self.exit_app.emit)

        # 运行菜单
        run_menu = self.addMenu("运行")
        run_menu.addAction("运行当前选中").triggered.connect(self.run_current.emit)
        run_menu.addAction("暂停").triggered.connect(self.pause_run.emit)
        run_menu.addAction("终止").triggered.connect(self.terminate_run.emit)
        run_menu.addSeparator()
        run_menu.addAction("跳转到作业页面").triggered.connect(
            self.goto_job_page.emit)

        # 窗口菜单
        window_menu = self.addMenu("窗口")
        window_menu.addAction("主页").triggered.connect(self.goto_home.emit)
        window_menu.addAction("数据集").triggered.connect(self.goto_dataset.emit)
        window_menu.addAction("模型").triggered.connect(self.goto_model.emit)
        window_menu.addAction("作业").triggered.connect(self.goto_job.emit)
        window_menu.addAction("训练").triggered.connect(self.goto_training.emit)
        window_menu.addAction("日志").triggered.connect(self.goto_log.emit)
        window_menu.addAction("评估").triggered.connect(
            self.goto_evaluation.emit)
        window_menu.addAction("导出").triggered.connect(self.goto_export.emit)

        # 帮助菜单
        help_menu = self.addMenu("帮助")
        help_menu.addAction("文档").triggered.connect(self.show_help.emit)
        help_menu.addAction("协议").triggered.connect(self.show_help.emit)
        help_menu.addAction("关于").triggered.connect(self.show_about.emit)


class WorkspaceTitleBar(QWidget):
    """工作区标题栏"""

    close_clicked = Signal()
    minimize_clicked = Signal()
    maximize_clicked = Signal()

    def __init__(self, parent=None, project_name="未知项目"):
        super().__init__(parent)
        self.parent_window = parent
        self.dragging = False
        self.drag_position = (0, 0)
        self.project_name = project_name
        self._setup_ui()

    def _setup_ui(self):
        """设置标题栏UI"""
        self.setFixedHeight(40)
        self.setStyleSheet("""
            WorkspaceTitleBar {
                background-color: #2c3e50;
                border-bottom: 1px solid #34495e;
            }
        """)

        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

        # 菜单栏
        self.menu_bar = WorkspaceMenuBar(self)
        self.menu_bar.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.menu_bar)

        # 项目标题（居中）
        self.title_label = QLabel(self.project_name)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
                padding: 0px 20px;
            }
        """)
        self.title_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.title_label, 1)

        # 窗口控制按钮
        self._create_window_controls(layout)

    def _create_window_controls(self, layout):
        """创建窗口控制按钮"""
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(0)

        # 按钮基础样式
        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                color: #ecf0f1;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """

        # 最小化按钮
        min_btn = QPushButton("—")
        min_btn.setFixedSize(53, 40)  # 4:3比例，高度40
        min_btn.setStyleSheet(button_style)
        min_btn.clicked.connect(self.minimize_clicked.emit)
        controls_layout.addWidget(min_btn)

        # 最大化按钮
        self.max_btn = QPushButton("🗖")
        self.max_btn.setFixedSize(53, 40)
        self.max_btn.setStyleSheet(button_style)
        self.max_btn.clicked.connect(self.toggle_maximize)
        controls_layout.addWidget(self.max_btn)

        # 关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(53, 40)
        close_btn.setStyleSheet(button_style + """
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        close_btn.clicked.connect(self.close_clicked.emit)
        controls_layout.addWidget(close_btn)

        # 添加到主布局
        controls_widget = QWidget()
        controls_widget.setLayout(controls_layout)
        layout.addWidget(controls_widget)

    def toggle_maximize(self):
        self.maximize_clicked.emit()
        if self.window().isMaximized():
            self.max_btn.setText("🗗")
        else:
            self.max_btn.setText("🗖")

    def set_project_name(self, name):
        """设置项目名称"""
        self.project_name = name
        # 根据可用空间截断文字
        self._update_title_display()

    def _update_title_display(self):
        """更新标题显示，处理文字截断"""
        available_width = self.title_label.width() - 40  # 留出一些边距
        if available_width > 0:
            font_metrics = QFontMetrics(self.title_label.font())
            elided_text = font_metrics.elidedText(
                self.project_name,
                Qt.TextElideMode.ElideRight,
                available_width
            )
            self.title_label.setText(elided_text)
        else:
            self.title_label.setText(self.project_name)

    def resizeEvent(self, event):
        """窗口大小改变时更新标题显示"""
        super().resizeEvent(event)
        self._update_title_display()

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件 - 开始拖拽"""
        if event.button() == Qt.MouseButton.LeftButton and self.parent_window:
            self.dragging = True
            # 记录鼠标点击位置相对于窗口左上角的比例
            window_rect = self.parent_window.frameGeometry()
            mouse_pos = event.globalPosition().toPoint()
            self.drag_position = (
                (mouse_pos.x() - window_rect.left()) / window_rect.width(),
                (mouse_pos.y() - window_rect.top()) / window_rect.height()
            )
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件 - 拖拽窗口"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.dragging and self.parent_window:
            if self.window().isMaximized():
                self.toggle_maximize()
            mouse_pos = event.globalPosition().toPoint()
            window_rect = self.parent_window.frameGeometry()
            # 根据比例重新计算窗口左上角位置
            rel_x, rel_y = self.drag_position
            new_left = mouse_pos.x() - int(window_rect.width() * rel_x)
            new_top = mouse_pos.y() - int(window_rect.height() * rel_y)
            self.parent_window.move(new_left, new_top)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件 - 结束拖拽"""
        self.dragging = False
        
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.toggle_maximize()
            event.accept()