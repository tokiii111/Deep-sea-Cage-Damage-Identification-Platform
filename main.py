# -*- coding: utf-8 -*-
import sys
import os
import traceback
import time
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QFileDialog, QApplication, QMessageBox
from yolov8n import Ui_Form  # 由pyuic5生成的UI模块
from detection_thread import DetectionThread


class MainWindow(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.detection_thread = DetectionThread()
        self.current_result_index = 0
        self.batch_results = []
        # 新增：支持的图像和视频格式
        self.supported_image_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        self.supported_video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        self.init_components()

    def init_components(self):
        # -------------------------- 模型路径设置 --------------------------
        self.modelCombo.clear()
        self.modelCombo.addItem(r"C:\Users\zhouw\OneDrive\Desktop\ultralytics-main\runs\detect\train10\weights\best.pt")
        self.modelCombo.addItem("C:/Users/zhouw/OneDrive/Desktop/ultralytics-main/yolov8n.pt")
        self.modelCombo.addItem(r"F:\rubbish dectect.pt")

        # -------------------------- 检测模式添加视频选项 --------------------------
        # 保留原有模式并新增"视频文件"选项
        self.detectModeCombo.clear()
        self.detectModeCombo.addItem("批量")
        self.detectModeCombo.addItem("单文件")
        self.detectModeCombo.addItem("视频文件")  # 新增视频模式
        self.detectModeCombo.addItem("摄像头")

        # -------------------------- 窗口设置 --------------------------
        QApplication.instance().setQuitOnLastWindowClosed(False)

        # 控件样式优化
        self.fileInfoLabel.setWordWrap(True)
        self.targetInfoLabel.setWordWrap(True)
        self.confInfoLabel.setWordWrap(True)
        self.fpsInfoLabel.setWordWrap(True)
        self.logTextEdit.setReadOnly(True)
        self.label.setMinimumSize(350, 450)
        self.imagePreviewLabel.setMinimumSize(350, 450)
        self.label_3.setAlignment(Qt.AlignCenter)
        font = self.label_3.font()
        font.setPointSize(10)
        self.label_3.setFont(font)

        # 置信度联动
        self.confSlider.setRange(0, 100)
        self.confSpinBox.setRange(0.00, 1.00)
        self.confSpinBox.setSingleStep(0.01)
        self.confSlider.valueChanged.connect(self.slider_update_spin)
        self.confSpinBox.valueChanged.connect(self.spin_update_slider)
        self.confSlider.setValue(50)
        self.confSpinBox.setValue(0.5)

        # 按钮信号连接
        self.selectBtn.clicked.connect(self.choose_path)
        self.startBtn.clicked.connect(self.start_detection)
        self.pauseBtn.clicked.connect(self.toggle_pause)
        self.stopBtn.clicked.connect(self.stop_detection)
        self.clearLogBtn.clicked.connect(self.logTextEdit.clear)
        self.prevBtn.clicked.connect(self.show_previous)
        self.nextBtn.clicked.connect(self.show_next)
        self.saveBtn.clicked.connect(self.save_current_result)

        self.pauseBtn.setEnabled(False)
        self.stopBtn.setEnabled(False)

        # 线程信号连接
        self.detection_thread.finished.connect(self.on_detection_finished)
        self.detection_thread.error_occurred.connect(self.on_thread_error)
        self.detection_thread.progress_update.connect(self.update_progress_bar)
        self.detection_thread.log_update.connect(self.append_log)
        self.detection_thread.image_preview_update.connect(self.display_preview)
        self.detection_thread.detection_result_update.connect(self.display_detection)
        self.detection_thread.info_update.connect(self.update_statistics)

    def on_detection_finished(self):
        self.append_log("✅ 检测任务已全部完成！")
        self.startBtn.setEnabled(True)
        self.pauseBtn.setEnabled(False)
        self.stopBtn.setEnabled(False)
        self.pauseBtn.setText("暂停")
        self.progressBar.setValue(100)
        QMessageBox.information(self, "检测完成", "所有检测任务已执行完毕，可继续选择新任务！")

    def on_thread_error(self, error_msg):
        self.append_log(f"❌ 检测出错：{error_msg}")
        self.startBtn.setEnabled(True)
        self.pauseBtn.setEnabled(False)
        self.stopBtn.setEnabled(False)
        QMessageBox.critical(self, "检测错误", f"检测过程中发生错误：\n{error_msg}")

    # -------------------------- 核心修改：添加视频文件选择逻辑 --------------------------
    def choose_path(self):
        try:
            mode = self.detectModeCombo.currentText()
            path = ""
            if mode == "批量":
                path = QFileDialog.getExistingDirectory(self, "选择批量检测文件夹")
                if path and not self._has_valid_files(path, is_video=False):
                    QMessageBox.warning(self, "提示",
                                        f"所选文件夹内无有效图像（支持{', '.join(self.supported_image_formats)}）！")
                    path = ""
            elif mode == "单文件":
                path, _ = QFileDialog.getOpenFileName(
                    self, "选择单张检测图像", "",
                    f"图像文件 ({' '.join(['*' + fmt for fmt in self.supported_image_formats])})"
                )
            # 新增：视频文件选择
            elif mode == "视频文件":
                path, _ = QFileDialog.getOpenFileName(
                    self, "选择视频文件", "",
                    f"视频文件 ({' '.join(['*' + fmt for fmt in self.supported_video_formats])})"
                )
                if path:
                    QMessageBox.information(self, "提示", "视频加载中，请耐心等待...")
            elif mode == "摄像头":
                path = "0"
                QMessageBox.information(self, "提示", "已选择默认摄像头（索引0），若无法启动请检查设备连接！")

            if path:
                self.filePathLabel.setText(f"文件路径：{path}")
                self.append_log(f"已选择{mode}路径：{path}")
        except Exception as e:
            self.append_log(f"路径选择出错：{str(e)}")

    # 新增：区分图像和视频文件的有效性检查
    def _has_valid_files(self, folder_path, is_video=False):
        try:
            supported_formats = self.supported_video_formats if is_video else self.supported_image_formats
            for file in os.listdir(folder_path):
                if os.path.splitext(file)[1].lower() in supported_formats:
                    return True
            return False
        except Exception as e:
            self.append_log(f"检查文件夹出错：{str(e)}")
            return False

    def start_detection(self):
        try:
            if self.detection_thread.isRunning():
                QMessageBox.warning(self, "提示", "检测任务已在运行中！")
                return

            model_path = self.modelCombo.currentText()
            conf = self.confSpinBox.value()
            mode = self.detectModeCombo.currentText()
            target_path = self.filePathLabel.text().split("：")[-1].strip()

            # 验证模型路径
            if not os.path.exists(model_path):
                QMessageBox.critical(self, "错误", "模型文件不存在！请检查模型路径！")
                return

            # 验证目标路径（新增视频模式验证）
            if mode in ["批量", "单文件", "视频文件"]:
                if not target_path or not os.path.exists(target_path):
                    QMessageBox.critical(self, "错误", f"请先选择有效{mode}路径！")
                    return
                # 批量模式仅检查图像
                if mode == "批量" and not self._has_valid_files(target_path, is_video=False):
                    QMessageBox.critical(self, "错误", "批量文件夹内无有效图像！请重新选择！")
                    return

            # 启动前重置状态
            self.batch_results.clear()
            self.current_result_index = 0
            self.progressBar.setValue(0)
            self.startBtn.setEnabled(False)
            self.pauseBtn.setEnabled(True)
            self.stopBtn.setEnabled(True)
            self.append_log(f"🚀 启动{mode}检测（置信度：{conf}）")

            # 启动线程
            self.detection_thread.setup(model_path, conf, mode, target_path)
            self.detection_thread.start()
        except Exception as e:
            self.append_log(f"启动检测出错：{str(e)}")
            self.startBtn.setEnabled(True)
            self.pauseBtn.setEnabled(False)
            self.stopBtn.setEnabled(False)

    def toggle_pause(self):
        try:
            self.detection_thread.paused = not self.detection_thread.paused
            self.pauseBtn.setText("继续" if self.detection_thread.paused else "暂停")
            self.append_log("检测已暂停" if self.detection_thread.paused else "检测已继续")
        except Exception as e:
            self.append_log(f"暂停/继续出错：{str(e)}")

    def stop_detection(self):
        try:
            if self.detection_thread.isRunning():
                self.detection_thread.running = False
                self.detection_thread.wait()
                self.append_log("🛑 检测任务已手动停止")
            self.startBtn.setEnabled(True)
            self.pauseBtn.setEnabled(False)
            self.stopBtn.setEnabled(False)
            self.pauseBtn.setText("暂停")
            self.progressBar.setValue(0)
        except Exception as e:
            self.append_log(f"停止检测出错：{str(e)}")

    def display_preview(self, pixmap):
        if pixmap:
            scaled_pix = pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(scaled_pix)
            self.label.setAlignment(Qt.AlignCenter)

    def display_detection(self, pixmap):
        if pixmap:
            scaled_pix = pixmap.scaled(self.imagePreviewLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.imagePreviewLabel.setPixmap(scaled_pix)
            self.imagePreviewLabel.setAlignment(Qt.AlignCenter)

    def update_statistics(self, file_name, target_count, avg_conf, fps):
        try:
            self.fileInfoLabel.setText(f"📔文件：{file_name}")
            self.targetInfoLabel.setText(f"📌监测目标：{target_count}")
            self.confInfoLabel.setText(f"🔖平均置信度：{avg_conf:.2f}")
            self.fpsInfoLabel.setText(f"⏱️FPS: {fps:.1f}")

            if self.detectModeCombo.currentText() == "批量":
                preview = self.label.pixmap().copy() if self.label.pixmap() else QPixmap()
                result = self.imagePreviewLabel.pixmap().copy() if self.imagePreviewLabel.pixmap() else QPixmap()
                if not preview.isNull() and not result.isNull():
                    self.batch_results.append((preview, result, file_name, target_count, avg_conf, fps))
                    self.label_3.setText(f"{len(self.batch_results)}/{len(self.batch_results)}")
        except Exception as e:
            self.append_log(f"更新统计信息出错：{str(e)}")

    def show_previous(self):
        if self.batch_results and self.current_result_index > 0:
            self.current_result_index -= 1
            self.show_result(self.current_result_index)

    def show_next(self):
        if self.batch_results and self.current_result_index < len(self.batch_results) - 1:
            self.current_result_index += 1
            self.show_result(self.current_result_index)

    def show_result(self, index):
        try:
            preview, result, file, target, conf, fps = self.batch_results[index]
            self.display_preview(preview)
            self.display_detection(result)
            self.update_statistics(file, target, conf, fps)
            self.label_3.setText(f"{index + 1}/{len(self.batch_results)}")
        except Exception as e:
            self.append_log(f"显示结果出错：{str(e)}")

    # main.py 中，找到原 save_current_result 方法，替换为以下代码
    def save_current_result(self):
        try:
            # 校验是否有批量检测结果
            if not hasattr(self, 'batch_results') or len(self.batch_results) == 0:
                QMessageBox.warning(self, "提示", "暂无批量检测结果可保存！")
                return

            # 弹出文件夹选择框，让用户选择保存位置
            save_dir = QFileDialog.getExistingDirectory(self, "选择全部结果保存文件夹", "./批量检测结果")
            if not save_dir:  # 用户取消选择则退出
                return

            # 遍历所有批量检测结果，逐个保存
            success_num = 0  # 成功保存数
            fail_num = 0  # 失败数
            for idx, result_item in enumerate(self.batch_results):
                # 解析批量结果（根据你的代码中 batch_results 存储格式，通常是 (预览图, 检测结果图, 原文件名, ...)）
                preview_pix, result_pix, file_name, _, _, _ = result_item

                # 生成保存文件名（原文件名+序号，避免重复）
                file_base = os.path.splitext(os.path.basename(file_name))[0]  # 取原文件前缀
                save_path = os.path.join(save_dir, f"{file_base}_检测结果_{idx + 1}.png")

                # 保存图片
                try:
                    result_pix.save(save_path)
                    success_num += 1
                    self.append_log(f"✅ 保存全部结果：{save_path}")
                except Exception as e:
                    fail_num += 1
                    self.append_log(f"❌ 保存失败 {save_path}：{str(e)}")

            # 保存完成后弹窗提示
            tip_content = f"全部结果保存完成！\n✅ 成功：{success_num} 张\n❌ 失败：{fail_num} 张\n📂 保存路径：{save_dir}"
            self.append_log(f"📦 批量保存任务结束（总计{len(self.batch_results)}张，成功{success_num}张）")
            QMessageBox.information(self, "保存完成", tip_content)

        except Exception as e:
            self.append_log(f"⚠️ 保存全部结果出错：{str(e)}")
            QMessageBox.error(self, "错误", f"保存失败：{str(e)}")

    def append_log(self, log_text):
        current_time = time.strftime("%H:%M:%S", time.localtime())
        self.logTextEdit.append(f"[{current_time}] {log_text}")
        self.logTextEdit.moveCursor(self.logTextEdit.textCursor().End)

    def slider_update_spin(self, value):
        self.confSpinBox.setValue(value / 100.0)

    def spin_update_slider(self, value):
        self.confSlider.setValue(int(value * 100))

    def update_progress_bar(self, progress):
        self.progressBar.setValue(progress)

    def closeEvent(self, event):
        self.stop_detection()
        QApplication.instance().quit()
        event.accept()


if __name__ == "__main__":
    def except_hook(exc_type, exc_value, exc_traceback):
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        QMessageBox.critical(None, "程序异常", f"发生未预期错误：\n{str(exc_value)}")
        sys.exit(1)


    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
