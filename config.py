from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFileDialog

from constants import ADD_FOLDER_ICON


class ConfigScreen(QWidget):

    submitted = pyqtSignal(list)

    def __init__(self, library_folders=None):
        super().__init__()

        # Window config
        self.setWindowTitle('Configurações')
        self.setLayout(QVBoxLayout())
        self.setStyleSheet("background-color: #181818")
        self.setMinimumSize(300, 300)

        self.library_folders = library_folders if library_folders else []

        self.folder_container = self.create_folders_container()

        self.layout().addWidget(self.folder_container)

    def create_folders_container(self):
        container = QWidget()
        container_vertical = QVBoxLayout()
        container.setLayout(container_vertical)

        header = QWidget()
        header.setLayout(QHBoxLayout())

        label = QLabel('Diretórios atuais:')
        label.setStyleSheet('color: #F2F2F2')

        button_add = QPushButton(QIcon("./images/add_folder.png"), "")
        button_add.setStyleSheet("color: #F2F2F2; border-image : url({});".format(ADD_FOLDER_ICON))
        button_add.setFixedSize(24, 24)
        button_add.clicked.connect(self.add_folder)

        header.layout().addWidget(label)
        header.layout().addWidget(button_add)

        container.layout().addWidget(header)

        if self.library_folders:
            for folder in self.library_folders:
                label_folder = QLabel(str(folder))
                label_folder.setStyleSheet("color: #B3B3B3")
                container_vertical.addWidget(label_folder)

        button_submit = QPushButton('Aplicar')
        button_submit.setStyleSheet("color: #F2F2F2")
        button_submit.clicked.connect(self.on_submit)
        container.layout().addWidget(button_submit)

        return container

    def add_folder(self):
        dialog_folder = QFileDialog()
        dialog_folder.setFileMode(QFileDialog.DirectoryOnly)

        folder_path = dialog_folder.getExistingDirectory(self, 'Selecione uma pasta')
        if folder_path == '' or folder_path in self.library_folders:
            return

        self.library_folders.append(folder_path)

        # Deletes current folder container, recreates it, then add to layout
        # also updates the reference to the widget self.folder_container
        temp_container = self.create_folders_container()
        self.layout().replaceWidget(self.folder_container, temp_container)
        self.folder_container = temp_container

    def on_submit(self):
        self.setEnabled(False)
        self.submitted.emit(self.library_folders)
        self.close()
        self.setEnabled(True)
