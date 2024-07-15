import requests
import sys
import os
import re
import shutil
import threading
import datetime
import xml.etree.ElementTree as ET
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, \
    QPushButton, QFileDialog, QScrollArea, QTextEdit, QProgressBar, QMessageBox, QFrame
from PySide2.QtCore import Qt

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

        self.surfaceFlag = QLineEdit();
        self.timestamp = QLineEdit()

        self.autoTimestamp = QCheckBox()
        self.autoTimestamp.stateChanged.connect(self.updateAutoTimestamp)

        self.ngSuffix = QLineEdit()
        self.deleteButton = QPushButton("Delete")
        self.deleteButton.clicked.connect(self.deleteSelf)
        self.sendButton = QPushButton("Send")
        self.sendButton.clicked.connect(self.send_config)
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Source result directory"))
        layout.addWidget(self.pathEdit)
        layout.addWidget(self.browseButton)

        layout.addWidget(QLabel("Surface flag:"))
        layout.addWidget(self.surfaceFlag)
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
        layout.addWidget(QLabel("Result ng flag"))
        layout.addWidget(self.ngSuffix)
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
        self.surfaceFlag.setReadOnly(state == Qt.Checked)
        self.timestamp.setReadOnly(state == Qt.Checked)
        self.ngSuffix.setReadOnly(state == Qt.Checked)

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
            if prog > 100:
                prog = 100
            if prog < 0:
                prog = 0
            self.progressBar.setValue(prog)
        else:
            self.progressBar.setValue(0)
        QApplication.processEvents()

    def copyResult(self, src_folder, dst_folder):
        if not os.path.exists(src_folder):
            QMessageBox.warning("Source folder %s not exists" % src_folder)
            return
        
        if not os.path.exists(dst_folder):
            os.makedirs(dst_folder)

        total_files = sum([len(files) for _, _, files in os.walk(src_folder)])
        copied_files = 0
        lock = threading.Lock()

        def copy_callback():
            nonlocal copied_files
            with lock:
                copied_files += 1
                self.updateProgress(copied_files, total_files)

        def custom_copy_function(src, dst):
            shutil.copy2(src, dst)
            copy_callback()

        shutil.copytree(src_folder, dst_folder, dirs_exist_ok=True, copy_function=custom_copy_function)

    def send_config(self) -> None:
        # 在这里编写发送配置的逻辑
        print("Sending configuration:")
        print("Path:", self.pathEdit.text())
        print("TimeStamp:", self.surfaceFlag.text() + self.timestamp.text() + self.ngSuffix.text())
        print("autoTimestamp Checkbox:", self.autoTimestamp.isChecked())

        src_folder = self.pathEdit.text()
        print(" source directory is: " + src_folder)
        if os.path.exists(src_folder) and os.path.isdir(src_folder):
            report_xml = os.path.join(src_folder, "report.xml")
            if os.path.exists(report_xml) and os.path.isfile(report_xml):
                try:
                    tree = ET.parse(report_xml)
                    root = tree.getroot()
                    project_element = root.find('project-name')
                    project_name = None
                    if project_element is not None:
                        project_name = os.path.basename(project_element.text)
                        print(f'project name is: {project_name}')
                        project_name = "/home/aoi/aoi/run/results/" + project_name
                    else:
                        print('could not find project name')
                    if project_name:
                        src_timestamp = os.path.basename(src_folder)
                        print(f"source folder timestamp is: {src_timestamp}")
                        pattern = r"(B_)(\d{17})(_\d+_NG)?"
                        match = re.search(pattern, src_timestamp)
                        if match:
                            print('source folder format valid.')
                            dst_timestamp = None
                            if self.autoTimestamp.isChecked():
                                dst_date  = datetime.datetime.now().strftime("%Y%m%d")
                                dst_clock = datetime.datetime.now().strftime("%H%M%S%f")[:-3]
                                dst_timestamp = dst_date + dst_clock
                                dst_timestamp = re.sub(r"\d{17}", dst_timestamp, src_timestamp)
                                dst_folder = os.path.join(project_name, dst_date, dst_timestamp)
                            else:
                                manuel_timestamp = re.search(r"(\d{17})", self.timestamp.text())
                                if manuel_timestamp:
                                    dst_date = manuel_timestamp.group(1)
                                    dst_timestamp = self.surfaceFlag.text() + self.timestamp.text() + self.ngSuffix.text()
                                    dst_folder = os.path.join(project_name, dst_date, dst_timestamp)
                            print(f"destination timestamp is: {dst_timestamp}")
                            print(f"--> dst folder={dst_folder}")
                            self.copyResult(src_folder, dst_folder)
                        else:
                            print('Invalid source folder format.')

                except Exception as e:
                    print(f"process report_xml error: {str(e)}")
            else:
                QMessageBox.warning(None, "错误", "report.xml文件不存在")
        else:
            QMessageBox.warning(None, "错误", src_folder + "路径不存在")

    def sendResult(self) -> None:
        base_url = 'http://172.18.134.11:8194/tasks'
        url_params = {
            'address': '/home/aoi/aoi/run/results/gt-001/20240714/B_20240714060040972_1_NG',
            'model': 'Virtual_D',
            'version': 'v1.0.0'
        }

        params = '&'.join([f"{k}={v}" for k, v in url_params.items()])
        url = base_url + '?' + params
        print(url)

        response = requests.post(url, params)
        print(response.status_code)
        print(response.text)


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