"""
作业页面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QCheckBox, QListWidget, QListWidgetItem,
    QFrame, QScrollArea, QFormLayout, QSpinBox, QDoubleSpinBox,
    QTextEdit, QGroupBox, QSplitter, QDateTimeEdit, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QDateTime
from PySide6.QtGui import QFont, QIcon

from ...model.enums.dataset_target import DatasetTarget


class PlanListItem(QFrame):
    """计划列表项"""
    
    clicked = Signal(str)  # 点击信号，传递计划ID
    delete_requested = Signal(str)  # 删除信号，传递计划ID
    
    def __init__(self, plan_id="plan_001", plan_name="训练计划1", description="示例训练计划", 
                 status="未开始", parent=None):
        super().__init__(parent)
        self.plan_id = plan_id
        self.plan_name = plan_name
        self.description = description
        self.status = status
        self.is_selected = False  # 添加选中状态
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI"""
        self.setFixedHeight(80)
        self._update_style()  # 使用动态样式更新
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 8, 8)
        layout.setSpacing(8)
        
        # 主要信息区域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # 计划名称
        name_label = QLabel(self.plan_name)
        name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        info_layout.addWidget(name_label)
        
        # 描述
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 11px;
            }
        """)
        info_layout.addWidget(desc_label)
        
        # 状态
        status_label = QLabel(f"状态: {self.status}")
        status_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 10px;
            }
        """)
        info_layout.addWidget(status_label)
        
        layout.addLayout(info_layout, 1)
        
        # 删除按钮
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(24, 24)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.plan_id))
        layout.addWidget(delete_btn)
    
    def _update_style(self):
        """更新样式"""
        if self.is_selected:
            style = """
                PlanListItem {
                    background-color: #4a9eff;
                    border: 2px solid #007acc;
                    border-radius: 6px;
                    margin: 2px;
                }
                PlanListItem:hover {
                    background-color: #5aafff;
                    border-color: #0088dd;
                }
                QLabel {
                    background-color: transparent;
                    color: #ffffff;
                }
            """
        else:
            style = """
                PlanListItem {
                    background-color: #3a3a3a;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    margin: 2px;
                }
                PlanListItem:hover {
                    background-color: #404040;
                    border-color: #666666;
                }
                QLabel {
                    background-color: transparent;
                }
            """
        self.setStyleSheet(style)
    
    def set_selected(self, selected=True):
        """设置选中状态"""
        self.is_selected = selected
        self._update_style()
        
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.plan_id)
            

class DatasetTargetItem(QFrame):
    """数据集目标项"""
    
    remove_requested = Signal()  # 移除信号
    
    def __init__(self, dataset_name="COCO数据集", target_type=DatasetTarget.TRAIN, parent=None):
        super().__init__(parent)
        self.dataset_name = dataset_name
        self.target_type = target_type
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI"""
        self.setFixedHeight(50)
        self.setStyleSheet("""
            DatasetTargetItem {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 4px;
                margin: 1px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # 数据集名称
        name_label = QLabel(self.dataset_name)
        name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        # 组合方式标签
        target_label = QLabel("用作:")
        target_label.setStyleSheet("color: #cccccc; font-size: 11px;")
        layout.addWidget(target_label)
        
        # 数据集目标选择
        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "训练集 (TRAIN)",
            "验证集 (VAL)", 
            "测试集 (TEST)",
            "混合 (MIXED)",
            "不使用 (UNUSED)"
        ])
        
        # 设置当前选中项
        target_index = {
            DatasetTarget.TRAIN: 0,
            DatasetTarget.VAL: 1,
            DatasetTarget.TEST: 2,
            DatasetTarget.MIXED: 3,
            DatasetTarget.UNUSED: 4
        }.get(self.target_type, 0)
        self.target_combo.setCurrentIndex(target_index)
        
        self.target_combo.setStyleSheet("""
            QComboBox {
                background-color: #555555;
                color: #ffffff;
                border: 1px solid #777777;
                border-radius: 3px;
                padding: 4px;
                min-width: 120px;
                font-size: 11px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #555555;
                color: #ffffff;
                selection-background-color: #007acc;
            }
        """)
        layout.addWidget(self.target_combo)
        
        # 移除按钮
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(20, 20)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_btn.clicked.connect(self.remove_requested.emit)
        layout.addWidget(remove_btn)
        
    def get_target_type(self):
        """获取当前选择的目标类型"""
        index = self.target_combo.currentIndex()
        target_mapping = [
            DatasetTarget.TRAIN,
            DatasetTarget.VAL,
            DatasetTarget.TEST,
            DatasetTarget.MIXED,
            DatasetTarget.UNUSED
        ]
        return target_mapping[index] if index < len(target_mapping) else DatasetTarget.TRAIN


class PlanDetailPanel(QScrollArea):
    """计划详情面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_plan_id = None
        self.dataset_items = []
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI"""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #555555;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #888888;
                border-radius: 6px;
                min-height: 20px;
            }
        """)
        
        # 外层容器（用于居中）
        outer_widget = QWidget()
        outer_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        self.setWidget(outer_widget)
        
        # 外层布局（水平居中）
        outer_layout = QHBoxLayout(outer_widget)
        outer_layout.setContentsMargins(20, 20, 20, 20)  # 添加外边距
        
        # 添加左侧弹性空间
        outer_layout.addStretch()
        
        # 主容器（有最大宽度限制）
        self.content_widget = QWidget()
        self.content_widget.setMaximumWidth(1000)  # 最大宽度1000px
        self.content_widget.setMinimumWidth(600)  # 最小宽度600px
        self.content_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        outer_layout.addWidget(self.content_widget)
        
        # 添加右侧弹性空间
        outer_layout.addStretch()
        
        # 主布局
        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # 标题区域
        self._create_title_section()
        
        # 基础信息区域
        self._create_basic_info_section()
        
        # 预训练模型选择区域
        self._create_model_selection_section()
        
        # 数据集选择区域
        self._create_dataset_selection_section()
        
        # 训练参数区域
        self._create_training_params_section()
        
        # 验证参数区域
        self._create_validation_params_section()
        
        # 底部弹性空间
        self.main_layout.addStretch()
        
    def _create_title_section(self):
        """创建标题区域"""
        self.title_label = QLabel("请选择一个计划")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                background-color: #2a2a2a;
                border-radius: 8px;
            }
        """)
        self.main_layout.addWidget(self.title_label)
        
    def _create_basic_info_section(self):
        """创建基础信息区域"""
        basic_group = QGroupBox("基础信息")
        basic_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #363636;
            }
        """)
        
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(10)
        basic_layout.setContentsMargins(15, 20, 15, 15)
        
        # 计划名称
        self.name_edit = QLineEdit()
        self.name_edit.setStyleSheet(self._get_input_style())
        basic_layout.addRow("计划名称:", self.name_edit)
        
        # 任务类型
        self.task_type_combo = QComboBox()
        self.task_type_combo.addItems(["检测", "分类", "分割", "关键点"])
        self.task_type_combo.setStyleSheet(self._get_combo_style())
        basic_layout.addRow("任务类型:", self.task_type_combo)
        
        # 创建日期
        self.create_date_edit = QDateTimeEdit()
        self.create_date_edit.setDateTime(QDateTime.currentDateTime())
        self.create_date_edit.setEnabled(False)
        self.create_date_edit.setStyleSheet(self._get_input_style())
        basic_layout.addRow("创建日期:", self.create_date_edit)
        
        # 修改日期
        self.modify_date_edit = QDateTimeEdit()
        self.modify_date_edit.setDateTime(QDateTime.currentDateTime())
        self.modify_date_edit.setEnabled(False)
        self.modify_date_edit.setStyleSheet(self._get_input_style())
        basic_layout.addRow("修改日期:", self.modify_date_edit)
        
        self.main_layout.addWidget(basic_group)
        
    def _create_model_selection_section(self):
        """创建预训练模型选择区域"""
        model_group = QGroupBox("预训练模型选择")
        model_group.setStyleSheet(self._get_group_style())
        
        model_layout = QVBoxLayout(model_group)
        model_layout.setContentsMargins(15, 20, 15, 15)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "YOLOv8n - 轻量级检测模型",
            "YOLOv8s - 小型检测模型", 
            "YOLOv8m - 中型检测模型",
            "ResNet50 - 经典分类模型",
            "EfficientNet-B0 - 高效分类模型"
        ])
        self.model_combo.setStyleSheet(self._get_combo_style())
        model_layout.addWidget(self.model_combo)
        
        self.main_layout.addWidget(model_group)
        
    def _create_dataset_selection_section(self):
        """创建数据集选择区域"""
        dataset_group = QGroupBox("数据集选择")
        dataset_group.setStyleSheet(self._get_group_style())
        
        dataset_layout = QVBoxLayout(dataset_group)
        dataset_layout.setContentsMargins(15, 20, 15, 15)
        dataset_layout.setSpacing(10)
        
        # 添加数据集按钮
        add_dataset_btn = QPushButton("+ 添加数据集")
        add_dataset_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0099ff;
            }
        """)
        add_dataset_btn.clicked.connect(self._add_dataset_item)
        dataset_layout.addWidget(add_dataset_btn)
        
        # 数据集列表容器
        self.dataset_container = QWidget()
        self.dataset_layout = QVBoxLayout(self.dataset_container)
        self.dataset_layout.setContentsMargins(0, 0, 0, 0)
        self.dataset_layout.setSpacing(5)
        dataset_layout.addWidget(self.dataset_container)
        
        self.main_layout.addWidget(dataset_group)
        
    def _create_training_params_section(self):
        """创建训练参数区域"""
        training_group = QGroupBox("训练参数")
        training_group.setStyleSheet(self._get_group_style())
        
        training_layout = QFormLayout(training_group)
        training_layout.setSpacing(10)
        training_layout.setContentsMargins(15, 20, 15, 15)
        
        # 纪元
        self.epochs_spinbox = QSpinBox()
        self.epochs_spinbox.setRange(1, 1000)
        self.epochs_spinbox.setValue(100)
        self.epochs_spinbox.setStyleSheet(self._get_spinbox_style())
        training_layout.addRow("纪元:", self.epochs_spinbox)
        
        # 初始学习率
        self.learning_rate_spinbox = QDoubleSpinBox()
        self.learning_rate_spinbox.setRange(0.0001, 1.0)
        self.learning_rate_spinbox.setDecimals(4)
        self.learning_rate_spinbox.setSingleStep(0.001)
        self.learning_rate_spinbox.setValue(0.01)
        self.learning_rate_spinbox.setStyleSheet(self._get_spinbox_style())
        training_layout.addRow("初始学习率:", self.learning_rate_spinbox)
        
        # 图像输入大小
        self.image_size_spinbox = QSpinBox()
        self.image_size_spinbox.setRange(64, 2048)
        self.image_size_spinbox.setSingleStep(32)
        self.image_size_spinbox.setValue(640)
        self.image_size_spinbox.setStyleSheet(self._get_spinbox_style())
        training_layout.addRow("图像输入大小:", self.image_size_spinbox)
        
        # 批次大小
        self.batch_size_spinbox = QSpinBox()
        self.batch_size_spinbox.setRange(1, 128)
        self.batch_size_spinbox.setValue(16)
        self.batch_size_spinbox.setStyleSheet(self._get_spinbox_style())
        training_layout.addRow("批次大小:", self.batch_size_spinbox)
        
        # 额外训练参数（TOML片段）
        extra_label = QLabel("额外训练参数 (TOML):")
        extra_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        training_layout.addRow(extra_label)
        
        self.extra_params_edit = QTextEdit()
        self.extra_params_edit.setFixedHeight(100)
        self.extra_params_edit.setPlainText("""# 额外训练参数
# optimizer = "AdamW"
# weight_decay = 0.0005
# warmup_epochs = 3""")
        self.extra_params_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        training_layout.addRow(self.extra_params_edit)
        
        self.main_layout.addWidget(training_group)
        
    def _create_validation_params_section(self):
        """创建验证参数区域"""
        validation_group = QGroupBox("验证参数")
        validation_group.setStyleSheet(self._get_group_style())
        
        validation_layout = QFormLayout(validation_group)
        validation_layout.setSpacing(10)
        validation_layout.setContentsMargins(15, 20, 15, 15)
        
        # 置信度阈值
        self.conf_threshold_spinbox = QDoubleSpinBox()
        self.conf_threshold_spinbox.setRange(0.01, 1.0)
        self.conf_threshold_spinbox.setDecimals(2)
        self.conf_threshold_spinbox.setSingleStep(0.05)
        self.conf_threshold_spinbox.setValue(0.25)
        self.conf_threshold_spinbox.setStyleSheet(self._get_spinbox_style())
        validation_layout.addRow("置信度阈值:", self.conf_threshold_spinbox)
        
        # IoU阈值
        self.iou_threshold_spinbox = QDoubleSpinBox()
        self.iou_threshold_spinbox.setRange(0.01, 1.0)
        self.iou_threshold_spinbox.setDecimals(2)
        self.iou_threshold_spinbox.setSingleStep(0.05)
        self.iou_threshold_spinbox.setValue(0.45)
        self.iou_threshold_spinbox.setStyleSheet(self._get_spinbox_style())
        validation_layout.addRow("IoU阈值:", self.iou_threshold_spinbox)
        
        self.main_layout.addWidget(validation_group)
        
    def _add_dataset_item(self):
        """添加数据集项"""
        # 模拟选择数据集（实际应该弹出选择对话框）
        dataset_names = ["COCO数据集", "ImageNet", "Pascal VOC", "自定义数据集1"]
        target_types = [DatasetTarget.TRAIN, DatasetTarget.VAL, DatasetTarget.TEST, DatasetTarget.MIXED]
        
        if len(self.dataset_items) < len(dataset_names):
            dataset_name = dataset_names[len(self.dataset_items)]
            target_type = target_types[len(self.dataset_items) % len(target_types)]
            item = DatasetTargetItem(dataset_name, target_type)
            item.remove_requested.connect(lambda: self._remove_dataset_item(item))
            self.dataset_items.append(item)
            self.dataset_layout.addWidget(item)
        
    def _remove_dataset_item(self, item):
        """移除数据集项"""
        if item in self.dataset_items:
            self.dataset_items.remove(item)
            item.setParent(None)
            
    def set_plan_data(self, plan_id, plan_data):
        """设置计划数据"""
        self.current_plan_id = plan_id
        self.title_label.setText(f"{plan_data.get('name', '未知计划')}")
        self.name_edit.setText(plan_data.get('name', ''))
        # 这里应该加载更多数据...
        
    def _get_input_style(self):
        """获取输入框样式"""
        return """
            QLineEdit, QDateTimeEdit {
                background-color: #555555;
                color: #ffffff;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }
            QLineEdit:focus, QDateTimeEdit:focus {
                border-color: #007acc;
            }
        """
        
    def _get_combo_style(self):
        """获取下拉框样式"""
        return """
            QComboBox {
                background-color: #555555;
                color: #ffffff;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #555555;
                color: #ffffff;
                selection-background-color: #007acc;
            }
        """
        
    def _get_spinbox_style(self):
        """获取数字输入框样式"""
        return """
            QSpinBox, QDoubleSpinBox {
                background-color: #555555;
                color: #ffffff;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
                min-width: 80px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #007acc;
            }
        """
        
    def _get_group_style(self):
        """获取分组框样式"""
        return """
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #363636;
            }
        """


class JobPage(QWidget):
    """作业页面"""
    
    def __init__(self, project, project_manager, parent=None):
        super().__init__(parent)
        self.project = project
        self.project_manager = project_manager
        self.plan_items = []
        self._setup_ui()
        self._load_sample_plans()
    
    def _setup_ui(self):
        """设置UI"""
        # 主布局：水平分割器
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #202020;
            }
        """)
        main_layout.addWidget(splitter)

        # 左侧：计划列表
        self._create_plan_list_panel(splitter)

        # 右侧：计划详情
        self.detail_panel = PlanDetailPanel()
        splitter.addWidget(self.detail_panel)

        # 设置分割比例
        splitter.setSizes([300, 700])  # 左侧300px，右侧700px
        splitter.setStretchFactor(0, 0)  # 左侧不拉伸
        splitter.setStretchFactor(1, 1)  # 右侧可拉伸
        
    def _create_plan_list_panel(self, parent):
        """创建计划列表面板"""
        list_widget = QWidget()
        list_widget.setFixedWidth(300)
        list_widget.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                border-right: 1px solid #555555;
            }
        """)
        
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(10, 10, 10, 10)
        list_layout.setSpacing(10)
        
        # 标题和添加按钮
        header_layout = QHBoxLayout()
        
        title_label = QLabel("训练计划")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(title_label)
        
        add_plan_btn = QPushButton("+ 添加")
        add_plan_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: #ffffff;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34ce57;
            }
        """)
        add_plan_btn.clicked.connect(self._add_new_plan)
        header_layout.addWidget(add_plan_btn)
        
        list_layout.addLayout(header_layout)
        
        # 计划列表滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.plan_list_container = QWidget()
        self.plan_list_layout = QVBoxLayout(self.plan_list_container)
        self.plan_list_layout.setContentsMargins(0, 0, 0, 0)
        self.plan_list_layout.setSpacing(5)
        self.plan_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.plan_list_container)
        list_layout.addWidget(scroll_area)
        
        parent.addWidget(list_widget)
        
    def _load_sample_plans(self):
        """加载示例计划"""
        sample_plans = [
            {
                "id": "plan_001",
                "name": "COCO检测训练", 
                "description": "基于COCO数据集的目标检测训练",
                "status": "未开始"
            },
            {
                "id": "plan_002", 
                "name": "分类模型训练",
                "description": "图像分类模型的训练计划", 
                "status": "进行中"
            },
            {
                "id": "plan_003",
                "name": "分割模型训练",
                "description": "语义分割模型训练计划",
                "status": "已完成"
            }
        ]
        
        for plan_data in sample_plans:
            item = PlanListItem(
                plan_data["id"],
                plan_data["name"], 
                plan_data["description"],
                plan_data["status"]
            )
            item.clicked.connect(self._on_plan_selected)
            item.delete_requested.connect(self._on_plan_delete_requested)
            self.plan_items.append(item)
            self.plan_list_layout.addWidget(item)
            
        # 自动选择第一个计划（如果有计划的话）
        if self.plan_items:
            first_plan = self.plan_items[0]
            self._on_plan_selected(first_plan.plan_id)
            # 设置视觉选中状态
            self._update_plan_selection(first_plan.plan_id)
            
    def _on_plan_selected(self, plan_id):
        """计划选中事件"""
        # 更新选中状态
        self._update_plan_selection(plan_id)
        
        # 模拟计划数据
        plan_data = {
            "name": f"计划 {plan_id}",
            "task_type": "检测",
            "description": "示例训练计划"
        }
        self.detail_panel.set_plan_data(plan_id, plan_data)
    
    def _update_plan_selection(self, selected_plan_id):
        """更新计划选择状态"""
        for item in self.plan_items:
            item.set_selected(item.plan_id == selected_plan_id)
        
    def _on_plan_delete_requested(self, plan_id):
        """计划删除请求"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除计划 '{plan_id}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # 找到并移除计划项
            for item in self.plan_items:
                if item.plan_id == plan_id:
                    self.plan_items.remove(item)
                    item.setParent(None)
                    break
                    
    def _add_new_plan(self):
        """添加新计划"""
        plan_id = f"plan_{len(self.plan_items) + 1:03d}"
        item = PlanListItem(
            plan_id,
            f"新计划 {len(self.plan_items) + 1}",
            "新建的训练计划",
            "未开始"
        )
        item.clicked.connect(self._on_plan_selected)
        item.delete_requested.connect(self._on_plan_delete_requested)
        self.plan_items.append(item)
        self.plan_list_layout.addWidget(item)
        
        # 自动选中新计划
        self._on_plan_selected(plan_id)
