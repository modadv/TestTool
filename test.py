import requests
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QFileDialog, QScrollArea, QTextEdit, QProgressBar

class ConfigItem(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.pathEdit = QLineEdit()
        self.pathEdit.setReadOnly(True)
        self.browseButton = QPushButton("Browse")
        self.browseButton.clicked.connect(self.browsePath)
        self.textEdit = QLineEdit()
        self.checkBox = QCheckBox()
        self.textLabel = QLabel("Label")
        self.deleteButton = QPushButton("Delete")
        self.deleteButton.clicked.connect(self.deleteSelf)
        self.sendButton = QPushButton("Send")
        self.sendButton.clicked.connect(self.sendConfig)
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)

        layout.addWidget(self.pathEdit)
        layout.addWidget(self.browseButton)
        layout.addWidget(self.textEdit)
        layout.addWidget(self.checkBox)
        layout.addWidget(self.textLabel)
        layout.addWidget(self.deleteButton)
        layout.addWidget(self.sendButton)
        layout.addWidget(self.progressBar)

        self.setLayout(layout)

    def browsePath(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            self.pathEdit.setText(path)

    def deleteSelf(self):
        self.setParent(None)
        self.deleteLater()

    def sendConfig(self):
        # 在这里编写发送配置的逻辑
        print("Sending configuration:")
        print("Path:", self.pathEdit.text())
        print("Text:", self.textEdit.text())
        print("Checkbox:", self.checkBox.isChecked())
        self.sendResult()
        # 模拟进度条的进度
        for i in range(101):
            self.progressBar.setValue(i)
            QApplication.processEvents()
            # 在这里添加实际的发送逻辑

    def sendResult(self):
        base_url = 'http://192.168.50.153:8194/tasks';
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
        self.addButton = QPushButton("Add Configuration")
        self.addButton.clicked.connect(self.addConfig)
        layout.addWidget(self.addButton)

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollAreaContent = QWidget()
        self.scrollLayout = QVBoxLayout(scrollAreaContent)
        scrollArea.setWidget(scrollAreaContent)
        layout.addWidget(scrollArea)

        self.logTextEdit = QTextEdit()
        self.logTextEdit.setReadOnly(True)
        layout.addWidget(self.logTextEdit)

        self.setLayout(layout)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Configuration")

    def addConfig(self):
        configItem = ConfigItem()
        self.scrollLayout.addWidget(configItem)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec())