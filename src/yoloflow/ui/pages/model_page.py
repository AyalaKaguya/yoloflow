"""
模型页面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QCheckBox, QScrollArea, QFrame,
    QStackedWidget, QMenu, QFileDialog, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont, QAction


class ModelCard(QFrame):
    """模型卡片组件"""
    
    clicked = Signal(str)  # 点击卡片信号，传递模型名称
    
    def __init__(self, model_name="示例模型", model_type="检测", description="模型描述", 
                 params_count="11.2M", model_size="22.4MB", parent=None):
        super().__init__(parent)
        self.model_name = model_name
        self.model_type = model_type
        self.description = description
        self.params_count = params_count
        self.model_size = model_size
        self._setup_ui()
        
    def _setup_ui(self):
        """设置卡片UI"""
        self.setFixedHeight(120)  # 固定高度，宽度自适应
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            ModelCard {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 8px;
                margin: 2px;
            }
            ModelCard:hover {
                background-color: #404040;
                border-color: #666666;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # 左侧：模型图标区域（占位）
        icon_label = QLabel()
        icon_label.setFixedSize(80, 80)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border: 1px dashed #666666;
                border-radius: 4px;
                color: #888888;
                font-size: 10px;
            }
        """)
        icon_label.setText("模型\n图标")
        layout.addWidget(icon_label)
        
        # 中间：模型信息区域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # 模型名称和类型
        name_type_layout = QHBoxLayout()
        name_type_layout.setSpacing(8)
        
        name_label = QLabel(self.model_name)
        name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        name_type_layout.addWidget(name_label)
        
        type_badge = QLabel(self.model_type)
        type_badge.setFixedHeight(20)
        type_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        type_badge.setStyleSheet("""
            QLabel {
                background-color: #007acc;
                color: #ffffff;
                border-radius: 10px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: bold;
            }
        """)
        name_type_layout.addWidget(type_badge)
        name_type_layout.addStretch()
        
        info_layout.addLayout(name_type_layout)
        
        # 描述
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 12px;
            }
        """)
        info_layout.addWidget(desc_label)
        
        # 参数统计
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        params_label = QLabel(f"参数: {self.params_count}")
        params_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 11px;
            }
        """)
        stats_layout.addWidget(params_label)
        
        size_label = QLabel(f"大小: {self.model_size}")
        size_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 11px;
            }
        """)
        stats_layout.addWidget(size_label)
        
        stats_layout.addStretch()
        info_layout.addLayout(stats_layout)
        
        layout.addLayout(info_layout, 1)
        
        # 右侧：操作按钮区域
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(4)
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 快捷操作按钮
        export_btn = QPushButton("导出")
        export_btn.setFixedSize(60, 24)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0099ff;
            }
        """)
        actions_layout.addWidget(export_btn)
        
        train_btn = QPushButton("训练")
        train_btn.setFixedSize(60, 24)
        train_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34ce57;
            }
        """)
        actions_layout.addWidget(train_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.model_name)
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            
    def _show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)
        
        # 菜单项
        view_action = QAction("查看详情", self)
        export_action = QAction("导出", self)
        train_plan_action = QAction("创建训练计划", self)
        delete_action = QAction("删除", self)
        
        # 添加到菜单
        menu.addAction(view_action)
        menu.addAction(export_action)
        menu.addAction(train_plan_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        
        # 设置样式
        menu.setStyleSheet("""
            QMenu {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QMenu::item {
                padding: 6px 12px;
            }
            QMenu::item:selected {
                background-color: #555555;
            }
        """)
        
        # 连接信号（暂时为空实现）
        view_action.triggered.connect(lambda: self._on_view_details())
        export_action.triggered.connect(lambda: self._on_export())
        train_plan_action.triggered.connect(lambda: self._on_create_train_plan())
        delete_action.triggered.connect(lambda: self._on_delete())
        
        menu.exec(position)
        
    def _on_view_details(self):
        """查看详情"""
        print(f"查看模型详情: {self.model_name}")
        
    def _on_export(self):
        """导出模型"""
        print(f"导出模型: {self.model_name}")
        
    def _on_create_train_plan(self):
        """创建训练计划"""
        print(f"为模型创建训练计划: {self.model_name}")
        
    def _on_delete(self):
        """删除模型"""
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除模型 '{self.model_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            print(f"删除模型: {self.model_name}")


class ModelCategoryGroup(QGroupBox):
    """模型分类组"""
    
    def __init__(self, category_name="分类", parent=None):
        super().__init__(category_name, parent)
        self.category_name = category_name
        self.model_cards = []
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI"""
        self.setStyleSheet("""
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
        
        # 垂直布局存放模型卡片
        self.cards_layout = QVBoxLayout(self)
        self.cards_layout.setContentsMargins(8, 15, 8, 8)
        self.cards_layout.setSpacing(8)
        
    def add_model_card(self, card):
        """添加模型卡片"""
        self.model_cards.append(card)
        self.cards_layout.addWidget(card)
        
    def clear_models(self):
        """清空所有模型"""
        for card in self.model_cards:
            card.setParent(None)
        self.model_cards.clear()


class ModelDetailPage(QWidget):
    """模型详情页面"""
    
    back_clicked = Signal()  # 返回信号
    
    def __init__(self, model_name="", parent=None):
        super().__init__(parent)
        self.model_name = model_name
        self.name_label = None
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 顶部工具栏
        toolbar_layout = QHBoxLayout()
        
        # 返回按钮
        back_btn = QPushButton("← 返回")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        back_btn.clicked.connect(self.back_clicked.emit)
        toolbar_layout.addWidget(back_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 主内容区域
        content_layout = QVBoxLayout()
        content_layout.addStretch()
        
        # 模型名称
        self.name_label = QLabel(f"模型: {self.model_name}")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        content_layout.addWidget(self.name_label)
        
        # 占位提示
        placeholder_label = QLabel("模型详情页面\n（待实现）")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 16px;
                line-height: 1.5;
            }
        """)
        content_layout.addWidget(placeholder_label)
        
        content_layout.addStretch()
        layout.addLayout(content_layout)
        
    def set_model_name(self, name):
        """设置模型名称"""
        self.model_name = name
        if self.name_label:
            self.name_label.setText(f"模型: {name}")


class ModelPage(QWidget):
    """模型页面"""
    
    def __init__(self, project, project_manager, parent=None):
        super().__init__(parent)
        self.project = project
        self.project_manager = project_manager
        self._setup_ui()
        self._load_sample_models()
    
    def _setup_ui(self):
        """设置UI"""
        # 主布局 - 使用堆叠窗口来切换页面
        self.stacked_widget = QStackedWidget()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        
        # 模型列表页面
        self.model_list_page = self._create_model_list_page()
        self.stacked_widget.addWidget(self.model_list_page)
        
        # 模型详情页面
        self.model_detail_page = ModelDetailPage()
        self.model_detail_page.back_clicked.connect(self._back_to_list)
        self.stacked_widget.addWidget(self.model_detail_page)
        
        # 默认显示列表页面
        self.stacked_widget.setCurrentIndex(0)
        
    def _create_model_list_page(self):
        """创建模型列表页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        # 左侧按钮组
        left_buttons_layout = QHBoxLayout()
        left_buttons_layout.setSpacing(8)
        
        download_btn = QPushButton("在线模型")
        import_btn = QPushButton("导入")
        export_btn = QPushButton("导出")
        
        for btn in [download_btn, import_btn, export_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #555555;
                    color: #ffffff;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
            """)
        
        download_btn.clicked.connect(self._on_add_model)
        import_btn.clicked.connect(self._on_import_model)
        export_btn.clicked.connect(self._on_export_model)
        
        left_buttons_layout.addWidget(download_btn)
        left_buttons_layout.addWidget(import_btn)
        left_buttons_layout.addWidget(export_btn)
        left_buttons_layout.addStretch()
        
        # 右侧控件组
        right_controls_layout = QHBoxLayout()
        right_controls_layout.setSpacing(8)
        
        # 筛选下拉框
        filter_combo = QComboBox()
        filter_combo.addItems(["全部类型", "检测", "分类", "分割", "关键点"])
        filter_combo.setStyleSheet("""
            QComboBox {
                background-color: #555555;
                color: #ffffff;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 80px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #555555;
                color: #ffffff;
                selection-background-color: #666666;
            }
        """)
        
        # 多选框
        multi_select_cb = QCheckBox("多选")
        multi_select_cb.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #555555;
                border: 1px solid #777777;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border: 1px solid #007acc;
            }
        """)
        
        # 搜索框
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("搜索模型...")
        search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #555555;
                color: #ffffff;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                min-width: 200px;
            }
            QLineEdit::placeholder {
                color: #aaaaaa;
            }
        """)
        
        right_controls_layout.addWidget(filter_combo)
        right_controls_layout.addWidget(multi_select_cb)
        right_controls_layout.addWidget(search_edit)
        
        # 组合工具栏
        toolbar_layout.addLayout(left_buttons_layout)
        toolbar_layout.addLayout(right_controls_layout)
        layout.addLayout(toolbar_layout)
        
        # 模型列表滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
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
            QScrollBar::handle:vertical:hover {
                background-color: #aaaaaa;
            }
        """)
        
        # 模型分类容器
        self.models_container = QWidget()
        self.models_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        self.models_layout = QVBoxLayout(self.models_container)
        self.models_layout.setContentsMargins(0, 0, 0, 0)
        self.models_layout.setSpacing(16)
        self.models_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.models_container)
        layout.addWidget(scroll_area)
        
        return page
        
    def _load_sample_models(self):
        """加载示例模型"""
        # 预训练模型组
        pretrained_group = ModelCategoryGroup("预训练模型")
        pretrained_models = [
            ("YOLOv8n", "检测", "轻量级目标检测模型", "3.2M", "6.2MB"),
            ("YOLOv8s", "检测", "小型目标检测模型", "11.2M", "21.5MB"),
            ("YOLOv8m", "检测", "中型目标检测模型", "25.9M", "49.7MB"),
            ("ResNet50", "分类", "经典分类网络", "25.6M", "97.8MB"),
            ("EfficientNet-B0", "分类", "高效分类网络", "5.3M", "20.1MB"),
        ]
        
        for name, type_, desc, params, size in pretrained_models:
            card = ModelCard(name, type_, desc, params, size)
            card.clicked.connect(self._on_model_clicked)
            pretrained_group.add_model_card(card)
            
        self.models_layout.addWidget(pretrained_group)
        
        # 训练过的模型组
        trained_group = ModelCategoryGroup("训练过的模型")
        trained_models = [
            ("自定义YOLOv8-项目1", "检测", "在项目1数据上训练的模型", "11.2M", "21.5MB"),
            ("自定义分类器-A", "分类", "项目专用分类模型", "5.3M", "20.1MB"),
        ]

        for name, type_, desc, params, size in trained_models:
            card = ModelCard(name, type_, desc, params, size)
            card.clicked.connect(self._on_model_clicked)
            trained_group.add_model_card(card)
            
        self.models_layout.addWidget(trained_group)
        
        # 导入的模型组
        imported_group = ModelCategoryGroup("导入的模型")
        imported_models = [
            ("第三方检测模型", "检测", "从外部导入的检测模型", "18.5M", "35.2MB"),
        ]

        for name, type_, desc, params, size in imported_models:
            card = ModelCard(name, type_, desc, params, size)
            card.clicked.connect(self._on_model_clicked)
            imported_group.add_model_card(card)
            
        self.models_layout.addWidget(imported_group)
        
    def _on_model_clicked(self, model_name):
        """模型卡片点击事件"""
        self.model_detail_page.set_model_name(model_name)
        self.stacked_widget.setCurrentIndex(1)
        
    def _back_to_list(self):
        """返回模型列表"""
        self.stacked_widget.setCurrentIndex(0)
        
    def _on_add_model(self):
        """新增模型"""
        model_name = "新模型"
        self.model_detail_page.set_model_name(model_name)
        self.stacked_widget.setCurrentIndex(1)
        
    def _on_import_model(self):
        """导入模型"""
        file_dialog = QFileDialog()
        file_path = file_dialog.getOpenFileName(self, "选择模型文件", "", "模型文件 (*.pt *.onnx *.pth)")
        if file_path[0]:
            print(f"导入模型: {file_path[0]}")
        
    def _on_export_model(self):
        """导出模型"""
        print("导出选中的模型")

