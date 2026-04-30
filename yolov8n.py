# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1200, 700)

        # 2. 左侧功能区
        self.leftwidget = QtWidgets.QWidget(Form)
        self.leftwidget.setGeometry(QtCore.QRect(9, 9, 400, 680))
        self.leftwidget.setObjectName("leftwidget")

        # 模型选择区
        self.modelwidget = QtWidgets.QWidget(self.leftwidget)
        self.modelwidget.setGeometry(QtCore.QRect(10, 10, 380, 41))
        self.modelCombo = QtWidgets.QComboBox(self.modelwidget)
        self.modelCombo.setGeometry(QtCore.QRect(100, 10, 270, 25))
        self.modelCombo.addItem("")
        self.pushButton = QtWidgets.QPushButton(self.modelwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 10, 80, 25))

        # 置信度区
        self.widget_2 = QtWidgets.QWidget(self.leftwidget)
        self.widget_2.setGeometry(QtCore.QRect(10, 60, 380, 40))
        self.confSpinBox = QtWidgets.QDoubleSpinBox(self.widget_2)
        self.confSpinBox.setGeometry(QtCore.QRect(280, 10, 80, 25))
        self.pushButton_2 = QtWidgets.QPushButton(self.widget_2)
        self.pushButton_2.setGeometry(QtCore.QRect(10, 10, 80, 25))
        self.confSlider = QtWidgets.QSlider(self.widget_2)
        self.confSlider.setGeometry(QtCore.QRect(100, 10, 170, 20))

        # 监测源配置
        self.groupBox = QtWidgets.QGroupBox(self.leftwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 110, 380, 120))
        self.widget = QtWidgets.QWidget(self.groupBox)
        self.widget.setGeometry(QtCore.QRect(10, 20, 220, 21))
        self.widget.setObjectName("widget")
        self.pushButton_3 = QtWidgets.QPushButton(self.widget)
        self.pushButton_3.setGeometry(QtCore.QRect(0, 0, 90, 25))
        self.detectModeCombo = QtWidgets.QComboBox(self.groupBox)
        self.detectModeCombo.setGeometry(QtCore.QRect(110, 20, 120, 25))
        self.detectModeCombo.addItem("")
        self.detectModeCombo.addItem("")
        self.detectModeCombo.addItem("")
        self.selectBtn = QtWidgets.QPushButton(self.groupBox)
        self.selectBtn.setGeometry(QtCore.QRect(10, 50, 360, 30))
        self.filePathLabel = QtWidgets.QLabel(self.groupBox)
        self.filePathLabel.setGeometry(QtCore.QRect(10, 90, 360, 20))

        # 监测控制
        self.groupBox_2 = QtWidgets.QGroupBox(self.leftwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 240, 380, 100))
        self.startBtn = QtWidgets.QPushButton(self.groupBox_2)
        self.startBtn.setGeometry(QtCore.QRect(10, 20, 90, 30))
        self.pauseBtn = QtWidgets.QPushButton(self.groupBox_2)
        self.pauseBtn.setGeometry(QtCore.QRect(110, 20, 90, 30))
        self.stopBtn = QtWidgets.QPushButton(self.groupBox_2)
        self.stopBtn.setGeometry(QtCore.QRect(210, 20, 90, 30))
        self.progressBar = QtWidgets.QProgressBar(self.groupBox_2)
        self.progressBar.setGeometry(QtCore.QRect(10, 60, 360, 30))
        self.pushButton_5 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_5.setGeometry(QtCore.QRect(330, 60, 40, 30))

        # 运行日志
        self.groupBox_3 = QtWidgets.QGroupBox(self.leftwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 350, 380, 320))
        self.logTextEdit = QtWidgets.QTextEdit(self.groupBox_3)
        self.logTextEdit.setGeometry(QtCore.QRect(10, 25, 360, 260))
        self.clearLogBtn = QtWidgets.QPushButton(self.groupBox_3)
        self.clearLogBtn.setGeometry(QtCore.QRect(280, 290, 90, 25))

        # 3. 右侧预览区
        self.rightwidget = QtWidgets.QWidget(Form)
        self.rightwidget.setGeometry(QtCore.QRect(420, 9, 770, 680))
        self.rightwidget.setObjectName("rightwidget")

        # 右侧功能按钮区
        self.widget_3 = QtWidgets.QWidget(self.rightwidget)
        self.widget_3.setGeometry(QtCore.QRect(10, 10, 750, 40))
        self.pushButton_7 = QtWidgets.QPushButton(self.widget_3)
        self.pushButton_7.setGeometry(QtCore.QRect(10, 10, 100, 30))
        self.pushButton_8 = QtWidgets.QPushButton(self.widget_3)
        self.pushButton_8.setGeometry(QtCore.QRect(120, 10, 100, 30))
        self.pushButton_9 = QtWidgets.QPushButton(self.widget_3)
        self.pushButton_9.setGeometry(QtCore.QRect(230, 10, 100, 30))

        # 批量检测结果容器
        self.groupBox_4 = QtWidgets.QGroupBox(self.rightwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(10, 60, 750, 610))

        # ---------- 图片预览区 ----------
        self.widget_4 = QtWidgets.QWidget(self.groupBox_4)
        self.widget_4.setGeometry(QtCore.QRect(20, 40, 350, 450))
        self.label = QtWidgets.QLabel(self.widget_4)
        self.label.setGeometry(QtCore.QRect(0, 0, 350, 450))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        # 开启图片自动缩放
        self.label.setScaledContents(True)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)

        # ---------- 检测结果区 ----------
        self.widget_5 = QtWidgets.QWidget(self.groupBox_4)
        self.widget_5.setGeometry(QtCore.QRect(390, 40, 350, 450))
        self.imagePreviewLabel = QtWidgets.QLabel(self.widget_5)
        self.imagePreviewLabel.setGeometry(QtCore.QRect(0, 0, 350, 450))
        self.imagePreviewLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.imagePreviewLabel.setScaledContents(True)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.imagePreviewLabel.setFont(font)

        # 翻页/保存按钮
        self.prevBtn = QtWidgets.QPushButton(self.groupBox_4)
        self.prevBtn.setGeometry(QtCore.QRect(250, 510, 100, 30))
        self.nextBtn = QtWidgets.QPushButton(self.groupBox_4)
        self.nextBtn.setGeometry(QtCore.QRect(360, 510, 100, 30))
        self.saveBtn = QtWidgets.QPushButton(self.groupBox_4)
        self.saveBtn.setGeometry(QtCore.QRect(470, 510, 100, 30))

        # 页码标签
        self.label_3 = QtWidgets.QLabel(self.groupBox_4)
        self.label_3.setGeometry(QtCore.QRect(350, 10, 80, 30))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)

        # 信息标签
        self.fileInfoLabel = QtWidgets.QLabel(self.groupBox_4)
        self.fileInfoLabel.setGeometry(QtCore.QRect(20, 560, 150, 20))
        self.targetInfoLabel = QtWidgets.QLabel(self.groupBox_4)
        self.targetInfoLabel.setGeometry(QtCore.QRect(20, 590, 150, 20))
        self.confInfoLabel = QtWidgets.QLabel(self.groupBox_4)
        self.confInfoLabel.setGeometry(QtCore.QRect(200, 560, 150, 20))
        self.fpsInfoLabel = QtWidgets.QLabel(self.groupBox_4)
        self.fpsInfoLabel.setGeometry(QtCore.QRect(200, 590, 150, 20))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.modelCombo.setItemText(0,
                                    _translate("Form", "C:/Users/zhouw/OneDrive/Desktop/ultralytics-main/yolov8n.pt"))
        self.pushButton.setText(_translate("Form", "模型选择："))
        self.pushButton_2.setText(_translate("Form", "置信度阈值"))
        self.groupBox.setTitle(_translate("Form", "监测源配置"))
        self.pushButton_3.setText(_translate("Form", "检测模式："))
        self.detectModeCombo.setItemText(0, _translate("Form", "批量"))
        self.detectModeCombo.setItemText(1, _translate("Form", "摄像头"))
        self.detectModeCombo.setItemText(2, _translate("Form", "单文件"))
        self.selectBtn.setText(_translate("Form", "选择文件/文件夹📂"))
        self.filePathLabel.setText(_translate("Form", "文件路径："))
        self.groupBox_2.setTitle(_translate("Form", "监测控制："))
        self.startBtn.setText(_translate("Form", "开始监测"))
        self.pauseBtn.setText(_translate("Form", "暂停"))
        self.stopBtn.setText(_translate("Form", "停止"))
        self.pushButton_5.setText(_translate("Form", "进度："))
        self.groupBox_3.setTitle(_translate("Form", "运行日志"))
        self.clearLogBtn.setText(_translate("Form", "🗑️清除"))
        self.pushButton_7.setText(_translate("Form", "🖥️实时监测"))
        self.pushButton_8.setText(_translate("Form", "🔍批量结果"))
        self.pushButton_9.setText(_translate("Form", "📷实时监控"))
        self.groupBox_4.setTitle(_translate("Form", "🔍批量检测结果："))
        self.label.setText(_translate("Form", "图片预览"))
        self.imagePreviewLabel.setText(_translate("Form", "检测结果"))
        self.prevBtn.setText(_translate("Form", "⏮上一个"))
        self.nextBtn.setText(_translate("Form", "下一个⏭"))
        self.saveBtn.setText(_translate("Form", "保存结果📩"))
        self.label_3.setText(_translate("Form", "pagelabel"))
        self.fileInfoLabel.setText(_translate("Form", "📔文件："))
        self.targetInfoLabel.setText(_translate("Form", "📌监测目标："))
        self.confInfoLabel.setText(_translate("Form", "🔖平均置信度："))
        self.fpsInfoLabel.setText(_translate("Form", "⏱️FPS:"))