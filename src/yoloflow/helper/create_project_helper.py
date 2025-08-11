"""
辅助从创建项目助手创建项目的相关函数
"""

import os
from pathlib import Path
import sys
from typing import Optional

from ..model import Project, DatasetInfo, ModelInfo, DatasetTarget
from PySide6.QtWidgets import QMessageBox


GITHUB_ASSETS_REPO = "ultralytics/assets"
GITHUB_ASSETS_NAMES = frozenset(
    [f"yolov8{k}{suffix}.pt" for k in "nsmlx" for suffix in (
        "", "-cls", "-seg", "-pose", "-obb", "-oiv7")]
    + [f"yolo11{k}{suffix}.pt" for k in "nsmlx" for suffix in (
        "", "-cls", "-seg", "-pose", "-obb")]
    # detect models only currently
    + [f"yolo12{k}{suffix}.pt" for k in "nsmlx" for suffix in ("",)]
    + [f"yolov5{k}{resolution}u.pt" for k in "nsmlx" for resolution in ("", "6")]
    + [f"yolov3{k}u.pt" for k in ("", "-spp", "-tiny")]
    + [f"yolov8{k}-world.pt" for k in "smlx"]
    + [f"yolov8{k}-worldv2.pt" for k in "smlx"]
    + [f"yoloe-v8{k}{suffix}.pt" for k in "sml" for suffix in ("-seg", "-seg-pf")]
    + [f"yoloe-11{k}{suffix}.pt" for k in "sml" for suffix in ("-seg", "-seg-pf")]
    + [f"yolov9{k}.pt" for k in "tsmce"]
    + [f"yolov10{k}.pt" for k in "nsmblx"]
    + [f"yolo_nas_{k}.pt" for k in "sml"]
    + [f"sam_{k}.pt" for k in "bl"]
    + [f"sam2_{k}.pt" for k in "blst"]
    + [f"sam2.1_{k}.pt" for k in "blst"]
    + [f"FastSAM-{k}.pt" for k in "sx"]
    + [f"rtdetr-{k}.pt" for k in "lx"]
    + [
        "mobile_sam.pt",
        "mobileclip_blt.ts",
        "yolo11n-grayscale.pt",
        "calibration_image_sample_data_20x128x128x3_float32.npy.zip",
    ]
)
GITHUB_ASSETS_TAG = "v8.3.0"


def initialize_project(project: Project, datasets: list[DatasetInfo], models: list[ModelInfo], parent_widget=None) -> Project:
    """帮助快速的创建项目，并自动添加数据集和预训练模型"""
    for dataset in datasets:
        project.dataset_manager.import_dataset(
            source_path=dataset.path,
            dataset_name=dataset.name,
            dataset_type=dataset.dataset_type,
            description=dataset.description
        )

    for model in models:
        # 先检查本地是否有缓存
        local_file = Path.cwd().joinpath('pretrained').joinpath(model.filename)
        if not local_file.exists():
            if model.filename not in GITHUB_ASSETS_NAMES:
                # 既不是预定义的模型，也不是可以下载到的模型，报错并跳过
                QMessageBox.critical(
                    None, "错误", f"无法找到模型文件，已跳过: {model.filename}")
                continue
            # 下载预训练模型
            download_url = f"https://github.com/{GITHUB_ASSETS_REPO}/releases/download/{GITHUB_ASSETS_TAG}/{model.filename}"

            # 显示下载对话框
            success = _download_model_with_dialog(
                download_url, local_file, model.filename, parent_widget)
            if not success:
                continue

        # 将模型添加到项目
        project.model_manager.add_pretrained_model(local_file, model.filename)

        # 为选中模型创建计划
        plan = project.plan_manager.create_plan(
            f"训练 - {model.filename}", f"pretrain/{model.filename}")

        # 将数据集以混合模式添加到训练计划中
        for dataset in datasets:
            plan.add_dataset(dataset.name, DatasetTarget.MIXED)
            plan.save()
            
        project.save_config()

    return project


def _download_model_with_dialog(download_url: str, output_path: Path, filename: str, parent_widget=None) -> bool:
    """通过对话框下载模型"""
    from ..ui import show_model_download_dialog
    from PySide6.QtWidgets import QApplication

    download_success = False
    download_error = ""
    dialog_closed = False

    def on_download_completed(success: bool, message: str):
        nonlocal download_success, download_error, dialog_closed
        download_success = success
        download_error = message
        dialog_closed = True

    def on_download_cancelled():
        nonlocal dialog_closed
        dialog_closed = True

    # 显示下载对话框
    dialog = show_model_download_dialog(
        parent=parent_widget,
        download_url=download_url,
        output_path=output_path,
        filename=filename,
        title=f"下载模型 - {filename}",
        on_completed=on_download_completed,
        on_cancelled=on_download_cancelled
    )

    # 等待对话框关闭
    app = QApplication.instance()
    if app:
        while not dialog_closed:
            app.processEvents()

    if not download_success and download_error:
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(parent_widget, "下载失败",
                             f"模型下载失败: {download_error}")

    return download_success
