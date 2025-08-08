"""
模型下载进度对话框
"""

from typing import Callable, Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QFrame, QDialog
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont

from .components import CustomTitleBar


class DownloadWorker(QThread):
    """下载工作线程"""
    
    progress_updated = Signal(int)  # 进度更新信号
    status_updated = Signal(str)    # 状态更新信号
    download_finished = Signal(bool, str)  # 下载完成信号 (success, message)
    
    def __init__(self, download_url: str, output_path: Path, filename: str):
        super().__init__()
        self.download_url = download_url
        self.output_path = output_path
        self.filename = filename
        self._cancelled = False
    
    def cancel(self):
        """取消下载"""
        self._cancelled = True
    
    def run(self):
        """执行下载"""
        try:
            import requests
            from urllib.parse import urlparse
            
            # 确保输出目录存在
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.status_updated.emit("正在连接服务器...")
            
            # 发送HEAD请求获取文件大小
            response = requests.head(self.download_url, allow_redirects=True)
            if response.status_code != 200:
                self.download_finished.emit(False, f"无法访问下载链接: {response.status_code}")
                return
            
            total_size = int(response.headers.get('content-length', 0))
            
            self.status_updated.emit(f"开始下载 {self.filename}...")
            
            # 开始下载
            response = requests.get(self.download_url, stream=True, allow_redirects=True)
            if response.status_code != 200:
                self.download_finished.emit(False, f"下载失败: {response.status_code}")
                return
            
            downloaded_size = 0
            chunk_size = 8192
            
            with open(self.output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if self._cancelled:
                        self.download_finished.emit(False, "下载已取消")
                        return
                    
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 更新进度
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.progress_updated.emit(progress)
                        
                        # 更新状态
                        if total_size > 0:
                            mb_downloaded = downloaded_size / (1024 * 1024)
                            mb_total = total_size / (1024 * 1024)
                            self.status_updated.emit(
                                f"正在下载 {self.filename}... {mb_downloaded:.1f}MB / {mb_total:.1f}MB"
                            )
            
            self.status_updated.emit("下载完成")
            self.progress_updated.emit(100)
            self.download_finished.emit(True, "下载成功")
            
        except requests.exceptions.RequestException as e:
            self.download_finished.emit(False, f"网络错误: {str(e)}")
        except Exception as e:
            self.download_finished.emit(False, f"下载失败: {str(e)}")


class ModelDownloadDialog(QDialog):
    """模型下载进度对话框"""
    
    download_completed = Signal(bool, str)  # 下载完成信号 (success, message)
    download_cancelled = Signal()           # 下载取消信号
    
    def __init__(self, parent=None, title="下载模型"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        
        self.download_worker: Optional[DownloadWorker] = None
        self.is_downloading = False
        
        self._setup_ui(title)
        self._setup_connections()
    
    def _setup_ui(self, title: str):
        """设置UI"""
        self.setFixedSize(500, 200)
        
        # 主容器
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #34495e;
                border-radius: 8px;
            }
        """)
        
        # 自定义标题栏
        self.title_bar = CustomTitleBar(self, title)
        main_layout.addWidget(self.title_bar)
        
        # 内容区域
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #34495e;
                border-radius: 0px 0px 8px 8px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 20, 30, 30)
        content_layout.setSpacing(20)
        
        # 状态标签
        self.status_label = QLabel("准备下载...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 14px;
                background: transparent;
            }
        """)
        content_layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2c3e50;
                border-radius: 8px;
                text-align: center;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-size: 12px;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 6px;
            }
        """)
        content_layout.addWidget(self.progress_bar)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedSize(80, 32)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: #bdc3c7;
            }
        """)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.cancel_button)
        
        content_layout.addLayout(button_layout)
        main_layout.addWidget(content_widget)
    
    def _setup_connections(self):
        """设置信号连接"""
        self.title_bar.close_clicked.connect(self._on_close)
        self.cancel_button.clicked.connect(self._on_cancel)
    
    def start_download(self, download_url: str, output_path: Path, filename: str):
        """开始下载"""
        if self.is_downloading:
            return
        
        self.is_downloading = True
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"准备下载 {filename}...")
        
        # 创建下载线程
        self.download_worker = DownloadWorker(download_url, output_path, filename)
        self.download_worker.progress_updated.connect(self.progress_bar.setValue)
        self.download_worker.status_updated.connect(self.status_label.setText)
        self.download_worker.download_finished.connect(self._on_download_finished)
        
        self.download_worker.start()
    
    def _on_download_finished(self, success: bool, message: str):
        """下载完成处理"""
        self.is_downloading = False
        self.cancel_button.setEnabled(False)
        
        if success:
            self.status_label.setText(message)
            self.progress_bar.setValue(100)
        else:
            self.status_label.setText(f"下载失败: {message}")
        
        self.download_completed.emit(success, message)
        
        # 延迟关闭对话框
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1500, self.close)
    
    def _on_cancel(self):
        """取消下载"""
        if self.download_worker and self.is_downloading:
            self.download_worker.cancel()
            self.status_label.setText("正在取消下载...")
            self.cancel_button.setEnabled(False)
        else:
            self.download_cancelled.emit()
            self.close()
    
    def _on_close(self):
        """关闭对话框"""
        self._on_cancel()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.download_worker and self.is_downloading:
            self.download_worker.cancel()
            self.download_worker.wait(3000)  # 等待最多3秒
        event.accept()


# 便利函数
def show_model_download_dialog(
    parent=None,
    download_url: str = "",
    output_path: Optional[Path] = None,
    filename: str = "",
    title: str = "下载模型",
    on_completed: Optional[Callable[[bool, str], None]] = None,
    on_cancelled: Optional[Callable[[], None]] = None
) -> ModelDownloadDialog:
    """
    显示模型下载对话框
    
    Args:
        parent: 父窗口
        download_url: 下载链接
        output_path: 输出文件路径
        filename: 文件名
        title: 对话框标题
        on_completed: 下载完成回调函数 (success, message)
        on_cancelled: 下载取消回调函数
    
    Returns:
        ModelDownloadDialog: 对话框实例
    """
    dialog = ModelDownloadDialog(parent, title)
    
    if on_completed:
        dialog.download_completed.connect(on_completed)
    if on_cancelled:
        dialog.download_cancelled.connect(on_cancelled)
    
    dialog.show()
    
    if download_url and output_path and filename:
        dialog.start_download(download_url, output_path, filename)
    
    return dialog
