import requests
import sys
import os
import re
import shutil
import threading
import datetime
from loguru import logger


import xml.etree.ElementTree as ET
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, \
    QPushButton, QFileDialog, QScrollArea, QTextEdit, QProgressBar, QMessageBox, QFrame
from PySide2.QtCore import Qt
from inspector.utils import inspectorUtils

class ConfigItem(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.pathEdit = QLineEdit()
        self.pathEdit.setReadOnly(True)

        self.browseButton = QPushButton("Browse")
        self.browseButton.clicked.connect(self.browsePath)

        self.timestamp = QLineEdit()

        self.autoTimestamp = QCheckBox()
        self.autoTimestamp.stateChanged.connect(self.updateAutoTimestamp)

        self.deleteButton = QPushButton("Delete")
        self.deleteButton.clicked.connect(self.deleteSelf)
        self.sendButton = QPushButton("Send")
        self.sendButton.clicked.connect(self.sendConfig)
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Source result directory"))
        layout.addWidget(self.pathEdit)
        layout.addWidget(self.browseButton)

        layout.addWidget(QLabel("Surface flag:"))
        layoutWidget = QWidget()
        layoutWidget.setLayout(layout)
        main_layout.addWidget(layoutWidget)
        main_layout.addSpacing(0)

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Timestamp"))
        layout.addWidget(self.timestamp)
        layout.addWidget(self.autoTimestamp)
        layout.addWidget(QLabel("Auto set timestamp"))
        layoutWidget = QWidget()
        layoutWidget.setLayout(layout)
        main_layout.addWidget(layoutWidget)
        main_layout.addSpacing(0)

        layout = QHBoxLayout()
        layoutWidget = QWidget()
        layoutWidget.setLayout(layout)
        main_layout.addWidget(layoutWidget)
        main_layout.addSpacing(0)

        layout = QHBoxLayout()
        layout.addWidget(self.deleteButton)
        layout.addWidget(self.sendButton)
        layout.addWidget(self.progressBar)
        layoutWidget = QWidget()
        layoutWidget.setLayout(layout)
        main_layout.addWidget(layoutWidget)
        main_layout.addSpacing(0)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        self.setLayout(main_layout)

        self.setMaximumHeight(180)

        self.autoTimestamp.setChecked(True)
        self.updateAutoTimestamp(Qt.Checked)

    def updateAutoTimestamp(self, state):
        self.timestamp.setReadOnly(state == Qt.Checked)

    def browsePath(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            self.pathEdit.setText(path)

    def deleteSelf(self):
        self.setParent(None)
        self.deleteLater()

    def updateProgress(self, copied_files, total_files):
        if total_files > 0 and copied_files >= 0:
            prog = (copied_files / total_files) * 100
            prog = min(100, max(0, prog))
            if prog == 100:
                inspectorUtils.sendResult("http://192.168.31.241:8194/tasks", {
                    'address': self.pathEdit.text(),
                    'model': 'Virtual_D',
                    'version': 'v1.0.0'
                })
            self.progressBar.setValue(prog)
        else:
            self.progressBar.setValue(0)
        QApplication.processEvents()

    def sendConfig(self) -> None:
        # 在这里编写发送配置的逻辑
        print("Sending configuration:")
        print("Path:", self.pathEdit.text())
        print("TimeStamp:", self.timestamp.text())
        print("autoTimestamp Checkbox:", self.autoTimestamp.isChecked())

        src_dir = self.pathEdit.text()
        print(" source directory is: " + src_dir)
        if os.path.exists(src_dir) and os.path.isdir(src_dir):
            report_xml = os.path.join(src_dir, "report.xml")
            if os.path.exists(report_xml) and os.path.isfile(report_xml):
                try:
                    tree = ET.parse(report_xml)
                    project_path = inspectorUtils.getProjectPath(tree)
                    if project_path:
                        src_timestamp = os.path.basename(src_dir)
                        if src_timestamp:
                            time_info = src_timestamp.split("_")
                            if self.autoTimestamp.isChecked():
                                logger.info(f"Auto timestamp")
                                dst_date, dst_clock = inspectorUtils.getSplitTimestamp()
                                time_info[1] = dst_date + dst_clock
                                dst_dir = os.path.join(project_path, dst_date, "_".join(time_info))
                            else:
                                logger.info(f"Manuel timestamp")
                                timestamp = self.timestamp.text()
                                if timestamp:
                                    dst_date = timestamp[:8]
                                    time_info[1] = timestamp
                                    dst_dir = os.path.join(project_path, dst_date, "_".join(time_info))
                            
                            if dst_dir:
                                logger.info(f"Dest dir: {dst_dir}")
                                inspectorUtils.copyInspectResult(src_dir, dst_dir, self.updateProgress)
                            else:
                                logger.info(f"Invalid dst dir")
                        else:
                            logger.info("Invalid source folder format.")

                except Exception as e:
                    logger.info(f"Process report_xml error: {str(e)}")
            else:
                logger.info("report.xml文件不存在")
        else:
            logger.info(src_dir + "路径不存在")

class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        hLayout = QHBoxLayout()
        ipLabel = QLabel("IP Address:")
        self.ipLineEdit = QLineEdit()
        hLayout.addWidget(ipLabel)
        hLayout.addWidget(self.ipLineEdit)
        
        self.addButton = QPushButton("Add Configuration")
        self.addButton.clicked.connect(self.addConfig)
        hLayout.addWidget(self.addButton)
        
        layout.addLayout(hLayout)
        
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollAreaContent = QWidget()
        self.scrollLayout = QVBoxLayout(scrollAreaContent)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        scrollArea.setWidget(scrollAreaContent)
        layout.addWidget(scrollArea)

        self.logTextEdit = QTextEdit()
        self.logTextEdit.setReadOnly(True)
        layout.addWidget(self.logTextEdit)

        self.setLayout(layout)
        self.setGeometry(100, 100, 1280, 800)
        self.setWindowTitle("Configuration")

    def addConfig(self):
        configItem = ConfigItem()
        self.scrollLayout.addWidget(configItem)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec_())