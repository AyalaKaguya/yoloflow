"""
测试模型下载对话框
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from yoloflow.ui.model_download_dialog import ModelDownloadDialog, DownloadWorker, show_model_download_dialog


@pytest.fixture
def app():
    """创建QApplication实例"""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app


@pytest.fixture
def download_dialog(app):
    """创建ModelDownloadDialog实例"""
    dialog = ModelDownloadDialog(title="测试下载")
    yield dialog
    dialog.close()


class TestDownloadWorker:
    """测试下载工作线程"""
    
    def test_worker_initialization(self):
        """测试工作线程初始化"""
        url = "https://example.com/file.txt"
        path = Path("test_file.txt")
        filename = "test_file.txt"
        
        worker = DownloadWorker(url, path, filename)
        
        assert worker.download_url == url
        assert worker.output_path == path
        assert worker.filename == filename
        assert not worker._cancelled
    
    def test_worker_cancel(self):
        """测试工作线程取消"""
        worker = DownloadWorker("https://example.com/file.txt", Path("test.txt"), "test.txt")
        
        worker.cancel()
        
        assert worker._cancelled


class TestModelDownloadDialog:
    """测试模型下载对话框"""
    
    def test_dialog_initialization(self, download_dialog):
        """测试对话框初始化"""
        assert download_dialog.windowTitle() == ""  # FramelessWindow
        assert download_dialog.isModal()
        assert not download_dialog.is_downloading
        assert download_dialog.download_worker is None
    
    def test_dialog_ui_elements(self, download_dialog):
        """测试对话框UI元素"""
        assert download_dialog.status_label is not None
        assert download_dialog.progress_bar is not None
        assert download_dialog.cancel_button is not None
        assert download_dialog.title_bar is not None
        
        # 检查初始状态
        assert download_dialog.progress_bar.value() == 0
        assert download_dialog.status_label.text() == "准备下载..."
        assert download_dialog.cancel_button.isEnabled()
    
    @patch('yoloflow.ui.model_download_dialog.DownloadWorker')
    def test_start_download(self, mock_worker_class, download_dialog):
        """测试开始下载"""
        mock_worker = Mock()
        mock_worker_class.return_value = mock_worker
        
        url = "https://example.com/file.txt"
        path = Path("test_file.txt")
        filename = "test_file.txt"
        
        download_dialog.start_download(url, path, filename)
        
        assert download_dialog.is_downloading
        assert download_dialog.cancel_button.isEnabled()
        mock_worker_class.assert_called_once_with(url, path, filename)
        mock_worker.start.assert_called_once()
    
    def test_download_finished_success(self, download_dialog):
        """测试下载成功完成"""
        download_dialog.is_downloading = True
        
        download_dialog._on_download_finished(True, "下载成功")
        
        assert not download_dialog.is_downloading
        assert not download_dialog.cancel_button.isEnabled()
        assert download_dialog.status_label.text() == "下载成功"
        assert download_dialog.progress_bar.value() == 100
    
    def test_download_finished_failure(self, download_dialog):
        """测试下载失败"""
        download_dialog.is_downloading = True
        
        download_dialog._on_download_finished(False, "网络错误")
        
        assert not download_dialog.is_downloading
        assert not download_dialog.cancel_button.isEnabled()
        assert "下载失败: 网络错误" in download_dialog.status_label.text()
    
    @patch('yoloflow.ui.model_download_dialog.DownloadWorker')
    def test_cancel_download(self, mock_worker_class, download_dialog):
        """测试取消下载"""
        mock_worker = Mock()
        mock_worker_class.return_value = mock_worker
        download_dialog.download_worker = mock_worker
        download_dialog.is_downloading = True
        
        download_dialog._on_cancel()
        
        mock_worker.cancel.assert_called_once()
        assert download_dialog.status_label.text() == "正在取消下载..."
        assert not download_dialog.cancel_button.isEnabled()


class TestUtilityFunctions:
    """测试工具函数"""
    
    def test_show_model_download_dialog(self, app):
        """测试便利函数"""
        callback_called = False
        
        def on_completed(success, message):
            nonlocal callback_called
            callback_called = True
        
        dialog = show_model_download_dialog(
            title="测试对话框",
            on_completed=on_completed
        )
        
        assert dialog is not None
        assert isinstance(dialog, ModelDownloadDialog)
        
        # 模拟下载完成
        dialog._on_download_finished(True, "测试完成")
        
        dialog.close()


if __name__ == '__main__':
    pytest.main([__file__])
