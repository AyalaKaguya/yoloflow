"""
工作区窗口
用户进行项目开发和管理的主要区域
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QStackedWidget,
                               QApplication, QMessageBox, QPushButton, QMainWindow)
from PySide6.QtCore import QByteArray, Qt, Signal, QPoint
from PySide6.QtGui import QPixmap, QIcon, QCloseEvent

from ..model import Project
from ..service import ProjectManager

from .components.workspace_title_bar import WorkspaceTitleBar
from .components.workflow_bar import WorkflowBar
from .components.status_bar import StatusBar
from .pages import (HomePage, DatasetPage, ModelPage, JobPage,
                    TrainingPage, LogPage, EvaluationPage, ExportPage)

# Windows API 常量，用于 nativeEvent
# https://learn.microsoft.com/en-us/windows/win32/inputdev/wm-nchittest
# 消息常量
WM_NCCALCSIZE = 0x0083
WM_NCHITTEST = 0x0084
WM_GETMINMAXINFO = 0x0024
# 命中测试常量
HT_CAPTION = 2
HT_CLIENT = 1
HT_LEFT = 10
HT_RIGHT = 11
HT_TOP = 12
HT_TOPLEFT = 13
HT_TOPRIGHT = 14
HT_BOTTOM = 15
HT_BOTTOMLEFT = 16
HT_BOTTOMRIGHT = 17
# 窗口样式常量
WS_OVERLAPPEDWINDOW = 0x00CF0000


class WorkspaceWindow(QMainWindow):
    """工作区窗口"""

    closed = Signal()  # 窗口关闭信号

    def __init__(self, project: Project, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.project = project
        self.project_manager = project_manager
        self.pages = []
        self.border_width = 5
        self._setup_ui()
        self._connect_signals()
        self._update_project_info()

    def _setup_ui(self):
        """设置UI"""
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        # 创建中央容器widget
        self.central_widget = QWidget()
        self.central_widget.setObjectName("central_widget")
        self.setCentralWidget(self.central_widget)
        
        # 设置初始样式（非全屏状态）
        self._update_window_style()

        # 主布局
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶栏：标题栏
        self.title_bar = WorkspaceTitleBar(
            self, self.project.name if self.project else "未知项目")
        main_layout.addWidget(self.title_bar)

        # 工作流栏
        self.workflow_bar = WorkflowBar()
        main_layout.addWidget(self.workflow_bar)

        # 主窗口：页面容器
        self.page_container = QStackedWidget()
        main_layout.addWidget(self.page_container, 1)

        # 状态栏
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)

        # 创建页面
        self._create_pages()

    def _update_window_style(self):
        """根据窗口状态更新样式"""
        if self.isMaximized():
            # 全屏状态：直角，无边框
            style = """
                #central_widget {
                    background-color: #363636;
                    border: none;
                    border-radius: 0px;
                }
                QStackedWidget{
                    background-color: #2b2b2b;
                    margin: 0px;
                }
                QWidget {
                    color: #ffffff;
                }
            """
        else:
            # 非全屏状态：圆角，半透明边框
            style = """
                #central_widget {
                    background-color: #363636;
                    border: 1px solid rgba(255, 255, 255, 77);
                    border-radius: 10px;
                }
                QStackedWidget{
                    background-color: #2b2b2b;
                    margin: 1px;
                }
                QWidget {
                    color: #ffffff;
                }
            """
        self.central_widget.setStyleSheet(style)

    def _create_pages(self):
        """创建所有页面"""
        page_classes = [
            HomePage, DatasetPage, ModelPage, JobPage,
            TrainingPage, LogPage, EvaluationPage, ExportPage
        ]

        for PageClass in page_classes:
            page = PageClass(self.project, self.project_manager, self)
            self.pages.append(page)
            self.page_container.addWidget(page)

        # 显示第一个页面
        if self.pages:
            self.page_container.setCurrentIndex(0)

    def _connect_signals(self):
        """连接信号"""
        # 标题栏信号
        self.title_bar.close_clicked.connect(self.close)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self._toggle_maximize)

        # 菜单栏信号
        menu_bar = self.title_bar.menu_bar
        menu_bar.new_project.connect(self._on_new_project)
        menu_bar.open_project.connect(self._on_open_project)
        menu_bar.project_manager.connect(self._on_project_manager)
        menu_bar.save_project.connect(self._on_save_project)
        menu_bar.save_as_project.connect(self._on_save_as_project)
        menu_bar.exit_app.connect(self._on_exit_app)

        menu_bar.run_current.connect(self._on_run_current)
        menu_bar.pause_run.connect(self._on_pause_run)
        menu_bar.terminate_run.connect(self._on_terminate_run)
        menu_bar.goto_job_page.connect(lambda: self._goto_page(3))

        menu_bar.goto_home.connect(lambda: self._goto_page(0))
        menu_bar.goto_dataset.connect(lambda: self._goto_page(1))
        menu_bar.goto_model.connect(lambda: self._goto_page(2))
        menu_bar.goto_job.connect(lambda: self._goto_page(3))
        menu_bar.goto_training.connect(lambda: self._goto_page(4))
        menu_bar.goto_log.connect(lambda: self._goto_page(5))
        menu_bar.goto_evaluation.connect(lambda: self._goto_page(6))
        menu_bar.goto_export.connect(lambda: self._goto_page(7))

        menu_bar.show_help.connect(self._on_show_help)
        menu_bar.show_about.connect(self._on_show_about)

        # 工作流栏信号
        self.workflow_bar.tab_changed.connect(self._on_tab_changed)
        self.workflow_bar.plan_selected.connect(self._on_plan_selected)
        self.workflow_bar.run_clicked.connect(self._on_run_current)
        self.workflow_bar.pause_clicked.connect(self._on_pause_run)
        self.workflow_bar.terminate_clicked.connect(self._on_terminate_run)

        # 状态栏信号
        self.status_bar.zoom_changed.connect(self._on_zoom_changed)

    def _update_project_info(self):
        """更新项目信息"""
        if self.project:
            # 更新标题
            self.title_bar.set_project_name(self.project.name)

            # 更新计划列表
            plans = []
            if hasattr(self.project, 'plan_manager') and self.project.plan_manager:
                all_plans = self.project.plan_manager.get_all_plans()
                plans = [plan.name for plan in all_plans]
            self.workflow_bar.update_plans(plans)

            # 更新状态
            self.status_bar.set_status_text(f"项目已加载: {self.project.name}")

    def _toggle_maximize(self):
        """切换最大化状态"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        # 状态变化后更新样式
        self._update_window_style()

    def changeEvent(self, event):
        """窗口状态变化事件"""
        super().changeEvent(event)
        if event.type() == event.Type.WindowStateChange:
            # 窗口状态变化时更新样式
            self._update_window_style()

    def _goto_page(self, index):
        """跳转到指定页面"""
        if 0 <= index < len(self.pages):
            self.workflow_bar.set_current_tab(index)
            self.page_container.setCurrentIndex(index)

    def _on_tab_changed(self, index):
        """Tab切换处理"""
        if 0 <= index < len(self.pages):
            self.page_container.setCurrentIndex(index)

            # 更新状态栏文本
            page_names = ["主页", "数据集", "模型", "作业", "训练", "日志", "评估", "导出"]
            if index < len(page_names):
                self.status_bar.set_status_text(f"当前页面: {page_names[index]}")

    def _on_plan_selected(self, plan_name):
        """计划选择处理"""
        self.status_bar.set_status_text(f"选择计划: {plan_name}")

    def _on_run_current(self):
        """运行当前选中的计划"""
        self.status_bar.set_status_text("开始运行...")
        self.workflow_bar.set_running_state(True)
        # TODO: 实现实际的运行逻辑

    def _on_pause_run(self):
        """暂停运行"""
        self.status_bar.set_status_text("运行已暂停")
        self.workflow_bar.set_running_state(False)
        # TODO: 实现实际的暂停逻辑

    def _on_terminate_run(self):
        """终止运行"""
        self.status_bar.set_status_text("运行已终止")
        self.workflow_bar.set_running_state(False)
        # TODO: 实现实际的终止逻辑

    def _on_zoom_changed(self, value):
        """缩放变化处理"""
        self.status_bar.set_zoom(value)
        # TODO: 实现实际的缩放逻辑

    # 菜单项处理函数（暂时为空实现）
    def _on_new_project(self):
        """新建项目"""
        self.status_bar.set_status_text("新建项目...")
        # TODO: 实现新建项目逻辑

    def _on_open_project(self):
        """打开项目"""
        self.status_bar.set_status_text("打开项目...")
        # TODO: 实现打开项目逻辑

    def _on_project_manager(self):
        """打开项目管理器"""
        self.status_bar.set_status_text("打开项目管理器...")
        # TODO: 实现打开项目管理器逻辑

    def _on_save_project(self):
        """保存项目"""
        if self.project:
            self.project.save_config()
            self.status_bar.set_status_text("项目已保存")
        else:
            self.status_bar.set_status_text("没有可保存的项目")

    def _on_save_as_project(self):
        """另存为项目"""
        self.status_bar.set_status_text("另存为...")
        # TODO: 实现另存为逻辑

    def _on_exit_app(self):
        """退出应用"""
        QApplication.quit()

    def _on_show_help(self):
        """显示帮助"""
        QMessageBox.information(self, "帮助", "YOLOFlow 帮助文档")

    def _on_show_about(self):
        """显示关于"""
        from ..__version__ import __version__
        QMessageBox.information(
            self, "关于", f"YOLOFlow v{__version__}\n\nYOLO项目工作流管理工具")

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 弹出保存确认对话框
        msg_box = QMessageBox()
        msg_box.setWindowTitle("关闭项目")
        msg_box.setText("是否保存项目更改？")
        msg_box.setInformativeText("项目可能包含未保存的更改。")

        # 添加自定义按钮
        save_button = msg_box.addButton(
            "保存", QMessageBox.ButtonRole.AcceptRole)
        discard_button = msg_box.addButton(
            "放弃", QMessageBox.ButtonRole.DestructiveRole)
        cancel_button = msg_box.addButton(
            "取消", QMessageBox.ButtonRole.RejectRole)

        # 设置默认按钮
        msg_box.setDefaultButton(save_button)

        # 显示对话框并获取结果
        msg_box.exec()
        clicked_button = msg_box.clickedButton()

        if clicked_button == save_button:
            # 保存项目
            try:
                if self.project:
                    self.project.save_config()
                    self.status_bar.set_status_text("项目已保存")
                # 接受关闭事件，发出信号
                self.closed.emit()
                event.accept()
                # 直接退出应用
                QApplication.quit()
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存项目时发生错误：{str(e)}")
                # 即使保存失败，也询问是否要强制退出
                if QMessageBox.question(self, "确认退出", "保存失败，是否仍要退出？") == QMessageBox.StandardButton.Yes:
                    self.closed.emit()
                    event.accept()
                    QApplication.quit()
                else:
                    # 取消关闭
                    event.ignore()

        elif clicked_button == discard_button:
            # 放弃更改，直接关闭
            self.closed.emit()
            event.accept()
            QApplication.quit()

        elif clicked_button == cancel_button:
            # 取消关闭
            event.ignore()

    def nativeEvent(self, eventType: QByteArray | bytes | bytearray | memoryview, message: int) -> object:
        if eventType == "windows_generic_MSG":
            try:
                from ctypes import wintypes, c_short
                msg = wintypes.MSG.from_address(int(message))

                # WM_NCCALCSIZE: 当窗口大小或位置改变时，可以修改客户区大小
                # 我们在这里阻止默认处理，以移除标准的窗口边框
                if msg.message == 0x0083:  # WM_NCCALCSIZE
                    # 当 wParam 为 TRUE 时，可以自定义客户区
                    # 返回 0 会使整个窗口都成为客户区
                    return True, 0

                # WM_NCHITTEST: 鼠标移动时，判断鼠标在窗口的哪个位置
                if msg.message == 0x0084 and not self.window().isMaximized():  # WM_NCHITTEST
                    # 获取鼠标相对于窗口左上角的坐标
                    # 注意：这里需要使用 signed int 来处理负数坐标（当鼠标在窗口外时）
                    x = c_short(msg.lParam & 0xFFFF).value
                    y = c_short(msg.lParam >> 16).value

                    pos = self.mapFromGlobal(QPoint(x, y))

                    # 判断是否在标题栏上 (用于拖动)
                    # if self.geometry().contains(pos):
                    #     return True, HT_CAPTION

                    # 判断是否在边框上 (用于缩放)
                    on_top = pos.y() >= 0 and pos.y() < self.border_width
                    on_bottom = pos.y() >= self.height() - self.border_width and pos.y() < self.height()
                    on_left = pos.x() >= 0 and pos.x() < self.border_width
                    on_right = pos.x() >= self.width() - self.border_width and pos.x() < self.width()

                    if on_top and on_left:
                        return True, HT_TOPLEFT
                    if on_top and on_right:
                        return True, HT_TOPRIGHT
                    if on_bottom and on_left:
                        return True, HT_BOTTOMLEFT
                    if on_bottom and on_right:
                        return True, HT_BOTTOMRIGHT
                    if on_top:
                        return True, HT_TOP
                    if on_bottom:
                        return True, HT_BOTTOM
                    if on_left:
                        return True, HT_LEFT
                    if on_right:
                        return True, HT_RIGHT
            except ImportError:
                pass

        return super().nativeEvent(eventType, message)
