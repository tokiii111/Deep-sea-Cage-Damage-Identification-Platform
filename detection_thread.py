import cv2
import time
import os
from ultralytics import YOLO
from PyQt5.QtCore import QThread, pyqtSignal, QMutex
from PyQt5.QtGui import QPixmap, QImage


class DetectionThread(QThread):
    # 原有信号保留，新增 error_occurred 信号（用于异常通知）
    progress_update = pyqtSignal(int)  # 进度更新信号（0-100）
    log_update = pyqtSignal(str)  # 日志更新信号
    image_preview_update = pyqtSignal(QPixmap)  # 原始图像预览信号
    detection_result_update = pyqtSignal(QPixmap)  # 检测结果图像信号
    info_update = pyqtSignal(str, int, float, float)  # 统一参数类型：文件名、目标数（int）、置信度（float）、FPS（float）
    error_occurred = pyqtSignal(str)  # 新增：线程异常通知信号

    def __init__(self):
        super().__init__()
        self.model_path = ""
        self.conf_threshold = 0.5
        self.detect_mode = ""
        self.file_path = ""
        self.running = True  # 运行标志
        self.paused = False  # 暂停标志
        self.mutex = QMutex()  # 线程安全锁
        self.model = None  # YOLO模型实例
        self.cap = None  # 视频/摄像头捕获对象（复用，统一管理资源）

    def setup(self, model_path, conf_threshold, detect_mode, file_path):
        """初始化检测参数（补充模型加载异常捕获）"""
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.detect_mode = detect_mode
        self.file_path = file_path
        self.running = True
        self.paused = False

        # 加载模型：补充异常捕获，避免模型加载失败导致程序崩溃
        try:
            self.model = YOLO(self.model_path)
            self.log_update.emit(f"模型加载成功：{os.path.basename(model_path)}")
        except Exception as e:
            self.model = None
            error_msg = f"模型加载失败：{str(e)}"
            self.log_update.emit(error_msg)
            self.error_occurred.emit(error_msg)  # 发射异常信号

    def run(self):
        """线程执行入口（补充全局异常捕获，新增视频模式判断）"""
        try:
            if not self.model:
                error_msg = "线程启动失败：模型未加载或加载错误"
                self.log_update.emit(error_msg)
                self.error_occurred.emit(error_msg)
                return

            # 根据检测模式执行对应逻辑（新增“视频文件”模式）
            if self.detect_mode == "批量":
                self._process_batch()
            elif self.detect_mode == "摄像头":
                self._process_camera()
            elif self.detect_mode == "单文件":
                self._process_single_file()
            elif self.detect_mode == "视频文件":  # 新增视频模式处理
                self._process_video()
            else:
                error_msg = f"不支持的检测模式：{self.detect_mode}"
                self.log_update.emit(error_msg)
                self.error_occurred.emit(error_msg)

        except Exception as e:
            # 捕获线程执行中的所有未预期异常
            error_msg = f"线程运行异常：{str(e)}"
            self.log_update.emit(error_msg)
            self.error_occurred.emit(error_msg)
        finally:
            # 确保视频/摄像头资源被释放（无论正常结束还是异常）
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
                self.cap = None

    # -------------------------- 新增：视频文件检测核心逻辑 --------------------------
    def _process_video(self):
        """处理视频文件：逐帧读取、检测、实时显示+进度更新"""
        try:
            # 1. 打开视频文件（区别于摄像头：直接传入文件路径字符串）
            self.cap = cv2.VideoCapture(self.file_path)
            if not self.cap.isOpened():
                error_msg = f"无法打开视频文件：{os.path.basename(self.file_path)}（请检查文件路径或格式）"
                self.log_update.emit(error_msg)
                self.error_occurred.emit(error_msg)
                return

            # 2. 获取视频基础信息（总帧数、帧率，用于进度计算和播放控制）
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 总帧数
            video_fps = self.cap.get(cv2.CAP_PROP_FPS)  # 视频原帧率（用于控制播放速度）
            if total_frames <= 0:
                error_msg = "视频文件无效：无法获取总帧数（可能是损坏文件）"
                self.log_update.emit(error_msg)
                self.error_occurred.emit(error_msg)
                self.cap.release()
                self.cap = None
                return

            self.log_update.emit(f"✅ 开始处理视频：{os.path.basename(self.file_path)}（总帧数：{total_frames}，原帧率：{round(video_fps,1)}）")
            frame_count = 0  # 当前已处理帧数
            start_time = time.time()  # 计时起点（用于计算实时FPS）

            # 3. 逐帧处理视频
            while self.running:
                # 处理暂停状态（线程安全：避免暂停时占用CPU）
                self.mutex.lock()
                while self.paused and self.running:
                    self.mutex.unlock()
                    self.msleep(100)  # 暂停时释放CPU，每100ms检查一次暂停状态
                    self.mutex.lock()
                self.mutex.unlock()

                # 4. 读取一帧视频（ret：是否成功，frame：帧数据）
                ret, frame = self.cap.read()
                if not ret:
                    # 两种情况：① 帧数读取完毕 ② 视频损坏
                    if frame_count >= total_frames:
                        self.log_update.emit("✅ 视频检测已完成所有帧！")
                    else:
                        self.log_update.emit(f"⚠️  视频检测中断：已处理{frame_count}/{total_frames}帧（可能是文件损坏）")
                    break

                # 5. 模型推理（检测当前帧）
                results = self.model(frame, conf=self.conf_threshold)
                annotated_frame = results[0].plot()  # 绘制检测框和类别标签

                # 6. 转换图像格式（OpenCV BGR → PyQt RGB，确保显示正常）
                preview_pix = self._cv2_to_qpixmap(frame)  # 原始帧预览
                result_pix = self._cv2_to_qpixmap(annotated_frame)  # 带检测框的帧

                # 7. 计算实时FPS（每10帧更新一次，避免频繁计算）
                frame_count += 1
                realtime_fps = 0.0
                if frame_count % 10 == 0:
                    elapsed_time = time.time() - start_time
                    if elapsed_time > 0:
                        realtime_fps = frame_count / elapsed_time
                    start_time = time.time()  # 重置计时起点

                # 8. 发送信号到主窗口（显示+统计信息）
                self.image_preview_update.emit(preview_pix)  # 原始帧显示
                self.detection_result_update.emit(result_pix)  # 检测结果显示
                self.info_update.emit(
                    os.path.basename(self.file_path),  # 视频文件名
                    len(results[0].boxes),  # 当前帧检测到的目标数
                    # 平均置信度（无目标时为0.0）
                    round(results[0].boxes.conf.mean().item(), 2) if len(results[0].boxes) > 0 else 0.0,
                    round(realtime_fps, 2)  # 实时FPS
                )

                # 9. 更新检测进度（按“已处理帧数/总帧数”计算百分比）
                progress = int((frame_count / total_frames) * 100)
                self.progress_update.emit(progress)

                # 10. 控制播放速度（匹配视频原帧率，避免播放过快）
                self.msleep(int(1000 / video_fps))  # 按原帧率计算每帧延迟（毫秒）

        except Exception as e:
            # 捕获视频检测中的异常（如文件读取错误、模型推理错误）
            error_msg = f"视频检测异常：{str(e)}"
            self.log_update.emit(error_msg)
            self.error_occurred.emit(error_msg)
        finally:
            # 确保视频资源被释放（无论正常结束还是异常）
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
                self.cap = None
            self.log_update.emit(f"🔌 视频资源已释放：{os.path.basename(self.file_path)}")

    # -------------------------- 原有逻辑保持不变（批量/单文件/摄像头） --------------------------
    def _process_batch(self):
        """批量处理文件夹中的图像（补充异常捕获）"""
        try:
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            # 过滤有效图像文件（处理文件夹访问权限异常）
            try:
                image_files = [f for f in os.listdir(self.file_path)
                               if os.path.splitext(f)[1].lower() in valid_extensions]
            except PermissionError:
                error_msg = "批量检测失败：无文件夹访问权限"
                self.log_update.emit(error_msg)
                self.error_occurred.emit(error_msg)
                return
            except Exception as e:
                error_msg = f"读取文件夹异常：{str(e)}"
                self.log_update.emit(error_msg)
                self.error_occurred.emit(error_msg)
                return

            total = len(image_files)
            if total == 0:
                self.log_update.emit("提示：文件夹中无有效图像文件！")
                return

            for i, file in enumerate(image_files, 1):
                # 检查是否需要停止线程
                if not self.running:
                    self.log_update.emit("批量检测已手动停止")
                    break
                # 处理暂停状态（线程安全）
                self.mutex.lock()
                while self.paused and self.running:
                    self.mutex.unlock()
                    self.msleep(100)  # 暂停时释放CPU资源
                    self.mutex.lock()
                self.mutex.unlock()

                # 处理单张图像
                full_path = os.path.join(self.file_path, file)
                self._process_single_image(full_path, file, i, total)

            # 仅当正常结束（未手动停止）时提示完成
            if self.running:
                self.log_update.emit("✅ 批量检测任务全部完成！")

        except Exception as e:
            error_msg = f"批量检测异常：{str(e)}"
            self.log_update.emit(error_msg)
            self.error_occurred.emit(error_msg)

    def _process_camera(self):
        """摄像头实时检测（完善资源释放+异常捕获）"""
        try:
            # 初始化摄像头（传入设备索引：整数）
            self.cap = cv2.VideoCapture(int(self.file_path))
            if not self.cap.isOpened():
                error_msg = f"无法打开摄像头（设备索引：{self.file_path}）"
                self.log_update.emit(error_msg)
                self.error_occurred.emit(error_msg)
                self.cap.release()
                self.cap = None
                return

            self.log_update.emit("📹 摄像头检测已启动（按停止按钮结束）")
            frame_count = 0
            start_time = time.time()

            while self.running:
                # 处理暂停状态
                self.mutex.lock()
                while self.paused and self.running:
                    self.mutex.unlock()
                    self.msleep(100)
                    self.mutex.lock()
                self.mutex.unlock()

                # 读取摄像头帧
                ret, frame = self.cap.read()
                if not ret:
                    if self.running:  # 仅当非手动停止时提示异常
                        self.log_update.emit("警告：摄像头帧读取失败（可能已断开连接）")
                    break

                frame_count += 1
                # 模型推理
                results = self.model(frame, conf=self.conf_threshold)
                annotated_frame = results[0].plot()  # 绘制检测框

                # 转换图像格式（避免OpenCV与PyQt格式冲突）
                preview_pix = self._cv2_to_qpixmap(frame)
                result_pix = self._cv2_to_qpixmap(annotated_frame)

                # 计算FPS（每10帧更新一次，避免频繁计算）
                fps = 0.0
                if frame_count % 10 == 0:
                    elapsed_time = time.time() - start_time
                    if elapsed_time > 0:
                        fps = frame_count / elapsed_time
                    frame_count = 0
                    start_time = time.time()

                # 发送实时数据到主窗口
                self.image_preview_update.emit(preview_pix)
                self.detection_result_update.emit(result_pix)
                self.info_update.emit("摄像头实时检测", len(results[0].boxes),
                                      results[0].boxes.conf.mean().item() if len(results[0].boxes) > 0 else 0.0,
                                      round(fps, 2))

                self.msleep(1)  # 控制刷新频率，避免CPU占用过高

        except Exception as e:
            error_msg = f"摄像头检测异常：{str(e)}"
            self.log_update.emit(error_msg)
            self.error_occurred.emit(error_msg)
        finally:
            # 确保摄像头资源被释放（无论正常结束还是异常）
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
                self.cap = None
            self.log_update.emit("🔌 摄像头资源已释放")

    def _process_single_file(self):
        """处理单个图像文件（补充文件存在性校验+异常捕获）"""
        try:
            if not os.path.exists(self.file_path):
                error_msg = f"单文件检测失败：文件不存在（{self.file_path}）"
                self.log_update.emit(error_msg)
                self.error_occurred.emit(error_msg)
                return

            file_name = os.path.basename(self.file_path)
            self._process_single_image(self.file_path, file_name, 1, 1)
            self.log_update.emit("✅ 单文件检测任务完成！")

        except Exception as e:
            error_msg = f"单文件检测异常：{str(e)}"
            self.log_update.emit(error_msg)
            self.error_occurred.emit(error_msg)

    def _process_single_image(self, path, name, current, total):
        """处理单张图像（通用方法，修复置信度计算空值问题）"""
        try:
            # 读取图像（处理损坏图像）
            frame = cv2.imread(path)
            if frame is None:
                self.log_update.emit(f"⚠️  跳过损坏图像：{name}")
                # 进度仍更新，避免卡住
                progress = int((current / total) * 100)
                self.progress_update.emit(progress)
                return

            # 模型推理计时
            start_time = time.time()
            results = self.model(frame, conf=self.conf_threshold)
            infer_time = time.time() - start_time
            fps = round(1 / infer_time, 2) if infer_time > 0 else 0.0

            # 处理检测结果（避免无目标时置信度计算报错）
            annotated_frame = results[0].plot()
            boxes = results[0].boxes
            target_count = len(boxes)
            avg_conf = round(boxes.conf.mean().item(), 2) if target_count > 0 else 0.0

            # 转换图像格式（确保PyQt能正常显示）
            preview_pix = self._cv2_to_qpixmap(frame)
            result_pix = self._cv2_to_qpixmap(annotated_frame)

            # 发送结果到主窗口
            self.image_preview_update.emit(preview_pix)
            self.detection_result_update.emit(result_pix)
            self.info_update.emit(name, target_count, avg_conf, fps)

            # 更新进度
            progress = int((current / total) * 100)
            self.progress_update.emit(progress)
            self.log_update.emit(f"✅ 图像 {name} 处理完成（进度：{progress}%）")

        except Exception as e:
            error_msg = f"处理图像 {name} 异常：{str(e)}"
            self.log_update.emit(error_msg)
            self.error_occurred.emit(error_msg)

    def _cv2_to_qpixmap(self, frame):
        """将OpenCV图像（BGR）转换为PyQt的QPixmap（修复图像翻转问题）"""
        try:
            # 转换BGR→RGB（OpenCV默认BGR，PyQt默认RGB）
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = rgb_frame.shape
            bytes_per_line = 3 * width
            # 创建QImage并转换为QPixmap（确保图像不翻转）
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            return QPixmap.fromImage(q_image)
        except Exception as e:
            self.log_update.emit(f"图像格式转换异常：{str(e)}")
            return QPixmap()  # 返回空Pixmap，避免主窗口报错

    def stop(self):
        """停止线程（完善资源释放，确保线程安全）"""
        self.mutex.lock()
        self.running = False
        self.paused = False  # 停止时解除暂停，避免线程卡在暂停循环
        self.mutex.unlock()

        # 释放视频/摄像头资源（如果存在）
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            self.cap = None

        # 等待线程退出（避免资源残留）
        self.wait()
        self.log_update.emit("🔚 检测线程已安全停止")