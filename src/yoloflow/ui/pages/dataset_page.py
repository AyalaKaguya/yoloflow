"""
数据集页面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QCheckBox, QScrollArea, QGridLayout,
    QFrame, QStackedWidget, QMenu, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont, QAction


class DatasetCard(QFrame):
    """数据集卡片组件"""
    
    clicked = Signal(str)  # 点击卡片信号，传递数据集名称
    
    def __init__(self, dataset_name="示例数据集", dataset_type="检测", description="数据集描述", parent=None):
        super().__init__(parent)
        self.dataset_name = dataset_name
        self.dataset_type = dataset_type
        self.description = description
        self._setup_ui()
        
    def _setup_ui(self):
        """设置卡片UI"""
        self.setFixedSize(280, 220)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            DatasetCard {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 8px;
            }
            DatasetCard:hover {
                background-color: #404040;
                border-color: #666666;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 图片区域（占位）
        image_label = QLabel()
        image_label.setFixedHeight(120)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border: 1px dashed #666666;
                border-radius: 4px;
                color: #888888;
            }
        """)
        image_label.setText("预览图片")
        layout.addWidget(image_label)
        
        # 信息区域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # 数据集名称
        name_label = QLabel(self.dataset_name)
        name_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        info_layout.addWidget(name_label)
        
        # 数据集类型
        type_label = QLabel(f"类型: {self.dataset_type}")
        type_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 12px;
            }
        """)
        info_layout.addWidget(type_label)
        
        # 描述
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 11px;
            }
        """)
        info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout)
        
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.dataset_name)
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            
    def _show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)
        
        # 菜单项
        view_action = QAction("查看详情", self)
        export_action = QAction("导出", self)
        settings_action = QAction("设置", self)
        delete_action = QAction("删除", self)
        
        # 添加到菜单
        menu.addAction(view_action)
        menu.addAction(export_action)
        menu.addAction(settings_action)
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
        settings_action.triggered.connect(lambda: self._on_settings())
        delete_action.triggered.connect(lambda: self._on_delete())
        
        menu.exec(position)
        
    def _on_view_details(self):
        """查看详情"""
        print(f"查看数据集详情: {self.dataset_name}")
        
    def _on_export(self):
        """导出数据集"""
        print(f"导出数据集: {self.dataset_name}")
        
    def _on_settings(self):
        """数据集设置"""
        print(f"数据集设置: {self.dataset_name}")
        
    def _on_delete(self):
        """删除数据集"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("确认删除")
        msg_box.setText(f"确定要删除数据集 '{self.dataset_name}' 吗？")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setStyleSheet("""
            QMessageBox {
                color: #000000;
            }
            QLabel {
                color: #000000;
            }
            QPushButton {
                color: #000000;
            }
        """)
        reply = msg_box.exec()
        if reply == QMessageBox.StandardButton.Yes:
            print(f"删除数据集: {self.dataset_name}")


class DatasetDetailPage(QWidget):
    """数据集详情页面（空白页）"""
    
    back_clicked = Signal()  # 返回信号
    
    def __init__(self, dataset_name="", parent=None):
        super().__init__(parent)
        self.dataset_name = dataset_name
        self.name_label = None  # 保存名称标签的引用
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
        
        # 数据集名称
        self.name_label = QLabel(f"数据集: {self.dataset_name}")
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
        placeholder_label = QLabel("数据集详情页面\n（待实现）")
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
        
    def set_dataset_name(self, name):
        """设置数据集名称"""
        self.dataset_name = name
        if self.name_label:
            self.name_label.setText(f"数据集: {name}")
        
    def _clear_layout(self):
        """清空布局"""
        pass  # 不需要了


class DatasetPage(QWidget):
    """数据集页面"""
    
    def __init__(self, project, project_manager, parent=None):
        super().__init__(parent)
        self.project = project
        self.project_manager = project_manager
        self._setup_ui()
        self._load_sample_datasets()
    
    def _setup_ui(self):
        """设置UI"""
        # 主布局 - 使用堆叠窗口来切换页面
        self.stacked_widget = QStackedWidget()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        
        # 数据集列表页面
        self.dataset_list_page = self._create_dataset_list_page()
        self.stacked_widget.addWidget(self.dataset_list_page)
        
        # 数据集详情页面
        self.dataset_detail_page = DatasetDetailPage()
        self.dataset_detail_page.back_clicked.connect(self._back_to_list)
        self.stacked_widget.addWidget(self.dataset_detail_page)
        
        # 默认显示列表页面
        self.stacked_widget.setCurrentIndex(0)
        
    def _create_dataset_list_page(self):
        """创建数据集列表页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        # 左侧按钮组
        left_buttons_layout = QHBoxLayout()
        left_buttons_layout.setSpacing(8)
        
        create_btn = QPushButton("创建")
        import_btn = QPushButton("导入")
        export_btn = QPushButton("导出")
        
        for btn in [create_btn, import_btn, export_btn]:
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
        
        create_btn.clicked.connect(self._on_create_dataset)
        import_btn.clicked.connect(self._on_import_dataset)
        export_btn.clicked.connect(self._on_export_dataset)
        
        left_buttons_layout.addWidget(create_btn)
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
        search_edit.setPlaceholderText("搜索数据集...")
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
        
        # 数据集网格区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # 网格容器
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.grid_widget)
        layout.addWidget(scroll_area)
        
        return page
        
    def _load_sample_datasets(self):
        """加载示例数据集"""
        sample_datasets = [
            ("COCO数据集", "检测", "通用目标检测数据集"),
            ("ImageNet", "分类", "图像分类基准数据集"),
            ("Pascal VOC", "分割", "语义分割数据集"),
            ("COCO关键点", "关键点", "人体关键点检测数据集"),
            ("自定义数据集1", "检测", "项目专用数据集"),
            ("自定义数据集2", "分类", "分类任务数据集"),
        ]
        
        for i, (name, type_, desc) in enumerate(sample_datasets):
            card = DatasetCard(name, type_, desc)
            card.clicked.connect(self._on_dataset_clicked)
            
            row = i // 4  # 每行4个
            col = i % 4
            self.grid_layout.addWidget(card, row, col)
            
    def _on_dataset_clicked(self, dataset_name):
        """数据集卡片点击事件"""
        self.dataset_detail_page.set_dataset_name(dataset_name)
        self.stacked_widget.setCurrentIndex(1)
        
    def _back_to_list(self):
        """返回数据集列表"""
        self.stacked_widget.setCurrentIndex(0)
        
    def _on_create_dataset(self):
        """创建数据集"""
        dataset_name = "新数据集"
        self.dataset_detail_page.set_dataset_name(dataset_name)
        self.stacked_widget.setCurrentIndex(1)
        
    def _on_import_dataset(self):
        """导入数据集"""
        file_dialog = QFileDialog()
        file_path = file_dialog.getExistingDirectory(self, "选择数据集文件夹")
        if file_path:
            print(f"导入数据集: {file_path}")
        
    def _on_export_dataset(self):
        """导出数据集"""
        print("导出选中的数据集")


