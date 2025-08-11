"""
Dataset configuration dialog

"""
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTextEdit, QFileDialog, QDialog, QFormLayout, QComboBox,
    QRadioButton, QMessageBox, QMainWindow
)
from PySide6.QtCore import Qt, Signal

from ..model.enums import TaskType, DatasetType
from ..model.project import DatasetInfo
from .components import CustomTitleBar
from .components.message_box import show_warning_message
from ..__version__ import __version__


class DatasetConfigDialog(QDialog):
    """数据集配置对话框"""

    def __init__(self, task_type: TaskType, parent=None):
        super().__init__(parent)
        self.task_type = task_type
        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        self.setWindowTitle("添加数据集")
        self.setFixedSize(450, 420)
        # 使用无框窗口
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 自定义标题栏
        self.title_bar = CustomTitleBar(self, "添加数据集")
        self.title_bar.close_clicked.connect(self.reject)
        main_layout.addWidget(self.title_bar)

        # 内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # 表单
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # 数据集名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入数据集名称")
        self.name_edit.setStyleSheet("""
            QLineEdit {
                background-color: #363636;
                color: white;
                border: 2px solid #999;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)

        name_label = QLabel("名称*:")
        name_label.setStyleSheet("color: white; font-weight: bold;")
        form_layout.addRow(name_label, self.name_edit)

        # 数据集类型
        self.type_combo = QComboBox()
        self.type_combo.addItems([self.task_type.value])  # 默认使用项目类型
        self.type_combo.setStyleSheet("""
            QComboBox {
                background-color: #363636;
                color: white;
                border: 2px solid #999;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                color: white;
            }
        """)

        type_label = QLabel("类型:")
        type_label.setStyleSheet("color: white; font-weight: bold;")
        form_layout.addRow(type_label, self.type_combo)

        # 数据集说明
        info_label = QLabel("📁 请选择已标注好的数据集（支持文件夹或压缩包格式）")
        info_label.setStyleSheet("""
            color: #ffd700; 
            font-size: 12px; 
            font-weight: bold; 
            background-color: #4a4a00; 
            border: 1px solid #ffd700; 
            border-radius: 4px; 
            padding: 8px; 
            margin-bottom: 10px;
        """)
        info_label.setWordWrap(True)
        content_layout.addWidget(info_label)

        # 数据集路径
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(
            "选择数据集文件夹或压缩包（支持 .zip, .rar, .7z 等格式）")
        self.path_edit.setStyleSheet("""
            QLineEdit {
                background-color: #363636;
                color: white;
                border: 2px solid #999;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)

        browse_folder_button = QPushButton("选择文件夹")
        browse_folder_button.clicked.connect(self._browse_dataset_folder)
        browse_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
        """)

        browse_file_button = QPushButton("选择压缩包")
        browse_file_button.clicked.connect(self._browse_dataset_file)
        browse_file_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_folder_button)
        path_layout.addWidget(browse_file_button)

        path_label = QLabel("数据集路径*:")
        path_label.setStyleSheet("color: white; font-weight: bold;")
        form_layout.addRow(path_label, path_layout)

        # 描述
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("输入数据集描述（可选）")
        self.description_edit.setFixedHeight(100)
        self.description_edit.setStyleSheet("""
            QTextEdit {
                background-color: #363636;
                color: white;
                border: 2px solid #999;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)

        desc_label = QLabel("描述:")
        desc_label.setStyleSheet("color: white; font-weight: bold;")
        form_layout.addRow(desc_label, self.description_edit)

        content_layout.addLayout(form_layout)

        # 按钮
        button_layout = QHBoxLayout()

        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)

        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self._validate_and_accept)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005999;
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)

        content_layout.addLayout(button_layout)
        main_layout.addWidget(content_widget)

        # 对话框整体样式
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)

    def _browse_dataset_folder(self):
        """浏览数据集文件夹"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择已标注的数据集文件夹",
            str(Path.home())
        )
        if dir_path:
            self.path_edit.setText(dir_path)

    def _browse_dataset_file(self):
        """浏览数据集压缩包"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择已标注的数据集压缩包",
            str(Path.home()),
            "压缩包文件 (*.zip *.rar *.7z *.tar *.gz *.bz2);;所有文件 (*.*)"
        )
        if file_path:
            self.path_edit.setText(file_path)

    def _validate_and_accept(self):
        """验证并接受"""
        if not self.name_edit.text().strip():
            show_warning_message(self, "验证错误", "请输入数据集名称")
            return

        if not self.path_edit.text().strip():
            show_warning_message(self, "验证错误", "请选择数据集路径（文件夹或压缩包）")
            return

        # 验证路径是否存在
        dataset_path = Path(self.path_edit.text().strip())
        if not dataset_path.exists():
            show_warning_message(self, "验证错误", "所选择的数据集路径不存在")
            return

        # 检查是文件夹还是文件
        if dataset_path.is_dir():
            # 是文件夹，检查是否为空
            if not any(dataset_path.iterdir()):
                show_warning_message(self, "验证错误", "所选择的数据集文件夹为空")
                return
        elif dataset_path.is_file():
            # 是文件，检查是否为支持的压缩包格式
            supported_extensions = {
                '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}
            if dataset_path.suffix.lower() not in supported_extensions:
                show_warning_message(
                    self, "验证错误", "请选择支持的压缩包格式（.zip, .rar, .7z, .tar, .gz, .bz2）")
                return
        else:
            show_warning_message(self, "验证错误", "请选择一个有效的文件夹或压缩包文件")
            return

        self.accept()

    def get_dataset_info(self) -> DatasetInfo:
        """获取数据集信息"""
        # 将 TaskType 转换为 DatasetType
        dataset_type = DatasetType(self.task_type.value)

        return DatasetInfo(
            name=self.name_edit.text().strip(),
            path=self.path_edit.text().strip(),  # 使用用户选择的实际路径
            dataset_type=dataset_type,
            description=self.description_edit.toPlainText().strip()
        )
