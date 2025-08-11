"""
Create New Project Wizard.

创建新项目向导窗口，包含Tab布局的多步骤项目配置界面。
"""

from pathlib import Path
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTextEdit, QFileDialog, QTabWidget, QGridLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QFormLayout, QComboBox,
    QSpacerItem, QSizePolicy, QScrollArea, QFrame, QButtonGroup,
    QRadioButton, QMessageBox, QMainWindow, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor



from ..model.enums import TaskType, DatasetType
from ..model.start_up import TaskTypeProvider, ModelSelector,ModelInfo
from ..model.project import DatasetInfo
from ..helper import initialize_project
from .components import CustomTitleBar
from .dataset_config_dialog import DatasetConfigDialog
from ..__version__ import __version__


class CreateProjectWizard(QMainWindow):
    """创建项目向导窗口"""

    # 信号：项目创建完成，传递项目路径
    project_created = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_provider = TaskTypeProvider()
        self.model_selector = ModelSelector()

        # 存储用户选择的数据
        self.selected_task_type: Optional[TaskType] = None
        self.project_name: str = ""
        self.project_description: str = ""
        self.project_path: str = ""
        self.datasets: List[DatasetInfo] = []
        self.selected_models: List[ModelInfo] = []
        
        # 用于跟踪模型列表是否需要更新
        self._last_task_type: Optional[TaskType] = None
        self._model_list_initialized = False

        self._setup_ui()
        self._setup_styles()

    def _setup_ui(self):
        """设置界面"""
        # 设置窗口属性 - 作为独立窗口但使用自定义标题栏
        self.setWindowTitle("创建新项目 - YOLOFlow")
        self.setFixedSize(800, 600)
        # 使用无框窗口但保持独立性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)

        # 创建中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 自定义标题栏
        self.title_bar = CustomTitleBar(self, "创建新项目")
        self.title_bar.close_clicked.connect(self.close)
        main_layout.addWidget(self.title_bar)

        # 内容区域
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_widget.setStyleSheet("""
            QWidget {
                background: transparent;
                color: #ffffff;
            }
        """)

        # Tab布局
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)  # Tab在左侧

        # 添加各个Tab页面
        self._create_task_type_page()
        self._create_project_info_page()
        self._create_dataset_config_page()
        self._create_model_config_page()

        content_layout.addWidget(self.tab_widget)
        main_layout.addWidget(content_widget)

        # 底部按钮区域
        self._create_bottom_buttons()
        main_layout.addWidget(self.button_widget)

        # 连接Tab切换信号
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # 初始状态
        self._update_button_state()

    def _create_task_type_page(self):
        """创建项目类型选择页面"""
        page = QWidget()
        layout = QVBoxLayout(page)

        # 标题
        title = QLabel("选择项目类型")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet(
            "color: white; font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # 说明文字
        description = QLabel("请选择您要创建的深度学习任务类型。不同的任务类型将影响可用的模型和配置选项。")
        description.setWordWrap(True)
        description.setStyleSheet(
            "color: #aaa; margin-bottom: 20px; font-size: 12px;")
        layout.addWidget(description)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)

        # 任务类型按钮组
        self.task_button_group = QButtonGroup()
        tasks = self.task_provider.get_all_tasks()

        # 按网格布局排列任务类型卡片
        rows = (len(tasks) + 1) // 2  # 每行2个
        for i, task_info in enumerate(tasks):
            row = i // 2
            col = i % 2

            # 创建任务卡片
            card = self._create_task_card(task_info)
            scroll_layout.addWidget(card, row, col)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # 添加到Tab
        self.tab_widget.addTab(page, "项目类型")

    def _create_task_card(self, task_info) -> QWidget:
        """创建任务类型卡片"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setFixedSize(300, 100)
        card.setStyleSheet("""
            QFrame {
                border: 2px solid #303030;
                border-radius: 8px;
                background-color: #303030;
                padding: 0px;
                color: white;
            }
            QFrame:hover {
                border-color: #007ACC;
            }
        """)

        layout = QVBoxLayout(card)

        # 单选按钮和标题
        header_layout = QHBoxLayout()
        radio = QRadioButton()
        # 使用自定义属性存储任务类型
        radio.setProperty("task_type", task_info.task_type)
        radio.setStyleSheet("""
            QRadioButton {
                font-weight: bold;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #ddd;
                background-color: transparent;
                border-radius: 9px;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #007ACC;
                background-color: #007ACC;
                border-radius: 9px;
            }
        """)
        self.task_button_group.addButton(radio)

        title = QLabel(task_info.name)
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: white; font-weight: bold; border: none;")

        header_layout.addWidget(radio)
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # 描述文字
        desc = QLabel(task_info.description)
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #aaa; font-size: 12px; border: none;")
        layout.addWidget(desc)

        # 点击卡片选中单选按钮
        def on_card_clicked():
            radio.setChecked(True)
            old_task_type = self.selected_task_type
            self.selected_task_type = task_info.task_type
            
            # 只有在任务类型真正改变时才重置已选择的模型
            if old_task_type != self.selected_task_type:
                self.selected_models.clear()
                self._last_task_type = self.selected_task_type
                self._model_list_initialized = False  # 标记需要重新初始化模型列表
                self._update_selected_models_display()
            
            self._update_button_state()

        card.mousePressEvent = lambda e: on_card_clicked()
        radio.clicked.connect(on_card_clicked)

        return card

    def _create_project_info_page(self):
        """创建项目信息页面"""
        page = QWidget()
        layout = QVBoxLayout(page)

        # 标题
        title = QLabel("项目信息")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet(
            "color: white; font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # 表单布局
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # 项目名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入项目名称")
        self.name_edit.textChanged.connect(self._on_project_info_changed)
        form_layout.addRow("项目名称*:", self.name_edit)

        # 项目描述
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("输入项目描述（可选）")
        self.description_edit.setFixedHeight(100)
        self.description_edit.textChanged.connect(
            self._on_project_info_changed)
        form_layout.addRow("项目描述:", self.description_edit)

        # 项目路径
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("选择项目保存路径")
        self.path_edit.textChanged.connect(self._on_project_info_changed)

        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self._browse_project_path)
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005999;
            }
        """)

        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_button)

        form_layout.addRow("保存路径*:", path_layout)

        layout.addLayout(form_layout)

        # 项目完整路径预览 - 直接添加到主布局以占满宽度
        self.full_path_label = QLabel("请填写项目名称和路径")
        self.full_path_label.setStyleSheet("""
            QLabel {
                color: #007ACC;
                background-color: #363636;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                margin-top: 10px;
                font-weight: bold;
            }
        """)
        self.full_path_label.setWordWrap(True)
        
        layout.addWidget(self.full_path_label)
        
        layout.addStretch()

        # 添加到Tab
        self.tab_widget.addTab(page, "项目信息")

    def _create_dataset_config_page(self):
        """创建数据集配置页面"""
        page = QWidget()
        layout = QVBoxLayout(page)

        # 标题
        title = QLabel("数据集配置")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet(
            "color: white; font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # 说明文字
        description = QLabel("配置项目将要使用的数据集。您也可以稍后添加。")
        description.setStyleSheet(
            "color: #aaa; margin-bottom: 20px; font-size: 12px;")
        layout.addWidget(description)

        # 添加按钮
        add_button = QPushButton("添加数据集")
        add_button.clicked.connect(self._add_dataset)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005999;
            }
        """)
        layout.addWidget(add_button)

        # 数据集表格
        self.dataset_table = QTableWidget()
        self.dataset_table.setColumnCount(6)
        self.dataset_table.setHorizontalHeaderLabels(
            ["名称", "任务类型", "数据类型", "路径", "描述", "操作"])

        # 设置表格属性
        header = self.dataset_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.dataset_table)

        # 添加到Tab
        self.tab_widget.addTab(page, "数据集配置")

    def _create_model_config_page(self):
        """创建模型配置页面"""
        page = QWidget()
        layout = QVBoxLayout(page)

        # 标题
        title = QLabel("模型配置")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet(
            "color: white; font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # 说明文字
        description = QLabel("选择适合您任务类型的预训练模型。您可以选择多个模型进行比较，也可以稍后添加。")
        description.setStyleSheet(
            "color: #aaa; margin-bottom: 20px; font-size: 12px;")
        layout.addWidget(description)
        
        # 已选择模型数量提示
        self.selected_models_label = QLabel("已选择模型: 0")
        self.selected_models_label.setStyleSheet(
            "color: #007ACC; margin-bottom: 10px; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.selected_models_label)

        # 模型列表将根据选择的任务类型动态更新
        self.model_list_widget = QWidget()
        self.model_list_layout = QVBoxLayout(self.model_list_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.model_list_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # 添加到Tab
        self.tab_widget.addTab(page, "模型配置")

    def _create_bottom_buttons(self):
        """创建底部按钮"""
        self.button_widget = QWidget()
        layout = QHBoxLayout(self.button_widget)

        # 左侧：取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.close)

        # 右侧：上一步、下一步/创建按钮
        layout.addWidget(self.cancel_button)
        layout.addStretch()

        self.prev_button = QPushButton("上一步")
        self.prev_button.clicked.connect(self._prev_step)
        self.prev_button.setEnabled(False)

        self.next_button = QPushButton("下一步")
        self.next_button.clicked.connect(self._next_step)

        layout.addWidget(self.prev_button)
        layout.addWidget(self.next_button)

    def _setup_styles(self):
        """设置样式 - 为每个组件单独设置样式"""
        # 主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)

        # Tab控件样式
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #3a3a3a;
            }
            QTabBar::tab {
                background-color: #2b2b2b;
                color: white;
                padding: 10px;
                margin-bottom: 2px;
            }
            QTabBar::tab:selected {
                background-color: #007ACC;
            }
        """)

        # 按钮样式
        button_style = """
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005999;
            }
            QPushButton:disabled {
                background-color: #666;
            }
        """

        # 应用按钮样式
        self.cancel_button.setStyleSheet(button_style)
        self.prev_button.setStyleSheet(button_style)
        self.next_button.setStyleSheet(button_style)

        # 输入框样式
        input_style = """
            background-color: #363636;
            color: white;
            border: 2px solid #999;
            border-radius: 4px;
            padding: 5px;
        """

        # 应用输入框样式
        self.name_edit.setStyleSheet(input_style)
        self.description_edit.setStyleSheet(input_style)
        self.path_edit.setStyleSheet(input_style)

        # 表格样式
        self.dataset_table.setStyleSheet("""
            QTableWidget {
                background-color: #363636;
                color: white;
                gridline-color: #ddd;
            }
        """)

    def _browse_project_path(self):
        """浏览项目路径"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择项目保存路径",
            str(Path.home())
        )
        if dir_path:
            self.path_edit.setText(dir_path)

    def _add_dataset(self):
        """添加数据集"""
        if self.selected_task_type is None:
            QMessageBox.warning(self, "错误", "请先选择项目类型")
            return

        dialog = DatasetConfigDialog(self.selected_task_type, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dataset_info = dialog.get_dataset_info()
            self.datasets.append(dataset_info)
            self._update_dataset_table()

    def _update_dataset_table(self):
        """更新数据集表格"""
        self.dataset_table.setRowCount(len(self.datasets))

        for row, dataset in enumerate(self.datasets):
            # 名称
            self.dataset_table.setItem(row, 0, QTableWidgetItem(dataset.name))
            # 任务类型
            self.dataset_table.setItem(
                row, 1, QTableWidgetItem(dataset.dataset_type.value))
            # 数据类型（文件夹或压缩包）
            dataset_path = Path(dataset.path)
            if dataset_path.is_dir():
                data_type = "📁 文件夹"
            else:
                data_type = "📦 压缩包"
            self.dataset_table.setItem(row, 2, QTableWidgetItem(data_type))
            # 路径
            self.dataset_table.setItem(row, 3, QTableWidgetItem(dataset.path))
            # 描述
            self.dataset_table.setItem(
                row, 4, QTableWidgetItem(dataset.description))
            # 删除按钮
            delete_button = QPushButton("删除")
            delete_button.clicked.connect(
                lambda checked, r=row: self._remove_dataset(r))
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            self.dataset_table.setCellWidget(row, 5, delete_button)

    def _remove_dataset(self, row: int):
        """删除数据集"""
        if 0 <= row < len(self.datasets):
            self.datasets.pop(row)
            self._update_dataset_table()

    def _update_model_list(self):
        """更新模型列表"""
        # 清空现有内容
        for i in reversed(range(self.model_list_layout.count())):
            item = self.model_list_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

        if not self.selected_task_type:
            return

        # 获取适合的模型
        models = self.model_selector.get_models_for_task(
            self.selected_task_type)

        for model in models:
            # 使用多选框而不是单选框
            checkbox = QCheckBox(f"{model.name} ({model.parameters})")
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: white;
                    padding: 5px;
                    font-weight: bold;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #ddd;
                    background-color: #2b2b2b;
                    border-radius: 4px;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #007ACC;
                    background-color: #007ACC;
                    border-radius: 4px;
                }
            """)
            # 使用自定义属性存储模型信息
            checkbox.setProperty("model_info", model)
            
            # 恢复之前的选择状态
            if model in self.selected_models:
                checkbox.setChecked(True)
            
            # 连接选择事件
            checkbox.stateChanged.connect(lambda state, m=model: self._on_model_selection_changed(state, m))

            # 添加描述
            desc_label = QLabel(model.description)
            desc_label.setStyleSheet(
                "color: #aaa; font-size: 11px; margin-left: 20px; margin-bottom: 10px;")
            desc_label.setWordWrap(True)

            self.model_list_layout.addWidget(checkbox)
            self.model_list_layout.addWidget(desc_label)

        self.model_list_layout.addStretch()
        
        # 更新选择计数显示
        self._update_selected_models_display()

    def _on_model_selection_changed(self, state, model):
        """模型选择改变时的处理"""
        from PySide6.QtCore import Qt
        
        if state == Qt.CheckState.Checked.value:
            # 添加模型到选择列表
            if model not in self.selected_models:
                self.selected_models.append(model)
        else:
            # 从选择列表中移除模型
            if model in self.selected_models:
                self.selected_models.remove(model)
        
        # 更新已选择模型数量显示
        self._update_selected_models_display()

    def _update_selected_models_display(self):
        """更新已选择模型的显示"""
        count = len(self.selected_models)
        if hasattr(self, 'selected_models_label'):
            if count == 0:
                self.selected_models_label.setText("已选择模型: 0")
                self.selected_models_label.setStyleSheet(
                    "color: #aaa; margin-bottom: 10px; font-size: 12px; font-weight: bold;")
            else:
                self.selected_models_label.setText(f"已选择模型: {count}")
                self.selected_models_label.setStyleSheet(
                    "color: #007ACC; margin-bottom: 10px; font-size: 12px; font-weight: bold;")

    def _on_project_info_changed(self):
        """项目信息改变时的处理"""
        self.project_name = self.name_edit.text().strip()
        self.project_description = self.description_edit.toPlainText().strip()
        self.project_path = self.path_edit.text().strip()
        
        # 更新完整路径显示
        self._update_full_path_display()
        
        self._update_button_state()
    
    def _update_full_path_display(self):
        """更新完整路径显示"""
        if self.project_name and self.project_path:
            # 构建完整路径
            full_path = Path(self.project_path) / self.project_name
            self.full_path_label.setText(f"项目将保存到: {full_path}")
            self.full_path_label.setStyleSheet("""
                QLabel {
                    color: #007ACC;
                    background-color: #363636;
                    border: 1px solid #007ACC;
                    border-radius: 4px;
                    padding: 8px;
                    margin-top: 10px;
                    font-weight: bold;
                }
            """)
        else:
            # 都没填写
            self.full_path_label.setText("请填写项目名称和路径")
            self.full_path_label.setStyleSheet("""
                QLabel {
                    color: #aaa;
                    background-color: #363636;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 8px;
                    margin-top: 10px;
                    font-weight: bold;
                }
            """)

    def _on_tab_changed(self, index):
        """Tab页面切换时的处理"""
        # 如果切换到模型配置页面且需要更新模型列表
        if index == 3 and self.selected_task_type:  # 模型配置页面索引为3
            # 只有在任务类型改变或首次进入时才更新模型列表
            if (not self._model_list_initialized or 
                self._last_task_type != self.selected_task_type):
                self._update_model_list()
                self._model_list_initialized = True
                self._last_task_type = self.selected_task_type
        # 更新按钮状态
        self._update_button_state()

    def _update_button_state(self):
        """更新按钮状态"""
        current_index = self.tab_widget.currentIndex()
        total_tabs = self.tab_widget.count()

        # 上一步按钮
        self.prev_button.setEnabled(current_index > 0)

        # 下一步/创建按钮
        if current_index == total_tabs - 1:
            self.next_button.setText("创建项目")
            self.next_button.setEnabled(self._can_create_project())
        else:
            self.next_button.setText("下一步")
            self.next_button.setEnabled(self._can_proceed_to_next())

    def _can_proceed_to_next(self) -> bool:
        """判断是否可以进行下一步"""
        current_index = self.tab_widget.currentIndex()

        if current_index == 0:  # 项目类型页面
            return self.selected_task_type is not None
        elif current_index == 1:  # 项目信息页面
            return bool(self.project_name and self.project_path)
        elif current_index == 2:  # 数据集配置页面
            return True  # 数据集是可选的
        else:
            return True

    def _can_create_project(self) -> bool:
        """判断是否可以创建项目"""
        return (self.selected_task_type is not None and
                bool(self.project_name and self.project_path))

    def _prev_step(self):
        """上一步"""
        current_index = self.tab_widget.currentIndex()
        if current_index > 0:
            self.tab_widget.setCurrentIndex(current_index - 1)
            # Tab切换会自动触发_on_tab_changed，无需再次调用_update_button_state

    def _next_step(self):
        """下一步或创建项目"""
        current_index = self.tab_widget.currentIndex()
        total_tabs = self.tab_widget.count()

        if current_index == total_tabs - 1:
            # 最后一步，创建项目
            self._create_project()
        else:
            # 进入下一步
            # 先验证当前页面是否可以进行下一步
            if not self._can_proceed_to_next():
                return
                
            self.tab_widget.setCurrentIndex(current_index + 1)
            # Tab切换会自动触发_on_tab_changed，无需再次调用_update_button_state

    def _create_project(self):
        """创建项目"""
        # 验证必要信息
        if self.selected_task_type is None:
            QMessageBox.warning(self, "错误", "请选择项目类型")
            return

        try:
            from ..model.project import Project

            # 构建项目路径
            full_project_path = Path(self.project_path) / self.project_name

            # 创建项目
            project = Project.create_new(
                project_path=str(full_project_path),  # 转换为字符串
                project_name=self.project_name,  # 使用正确的参数名
                task_type=self.selected_task_type,
                description=self.project_description
            )
            
            initialize_project(project, self.datasets, self.selected_models)
            # 保存配置
            project.save_config()

            # 发送信号
            self.project_created.emit(str(full_project_path))

            # 关闭窗口
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "创建项目失败", f"创建项目时发生错误：{str(e)}")
