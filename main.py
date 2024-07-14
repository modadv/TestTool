import requests
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, \
    QPushButton, QFileDialog, QScrollArea


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
        self.sendButton = QPushButton("Send")  # 添加发送按钮
        self.sendButton.clicked.connect(self.sendConfig)  # 连接发送按钮的点击事件

        layout.addWidget(self.pathEdit)
        layout.addWidget(self.browseButton)
        layout.addWidget(self.textEdit)
        layout.addWidget(self.checkBox)
        layout.addWidget(self.textLabel)
        layout.addWidget(self.deleteButton)
        layout.addWidget(self.sendButton)  # 将发送按钮添加到布局中

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

    def send

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

        self.setLayout(layout)
        self.setWindowTitle("Configuration")

    def addConfig(self):
        configItem = ConfigItem()
        self.scrollLayout.addWidget(configItem)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec())
