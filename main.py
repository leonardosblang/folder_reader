import sys
import os
from PyQt5.QtWidgets import QApplication, QFileDialog, QVBoxLayout, QPushButton, QDialog, QLabel, QTreeView, \
    QFileSystemModel
from PyQt5.QtCore import Qt, QItemSelectionModel


class FolderReader(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Folder Reader App")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()

        self.folder_label = QLabel("No folder selected yet.")
        layout.addWidget(self.folder_label)

        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.clicked.connect(self.open_folder)
        layout.addWidget(self.open_folder_button)

        self.tree = QTreeView()
        self.tree.setSelectionMode(QTreeView.ExtendedSelection)
        layout.addWidget(self.tree)

        self.model = QFileSystemModel()
        self.tree.setModel(self.model)
        self.tree.clicked.connect(self.folder_clicked)

        self.save_button = QPushButton("Save Selected Files' Contents")
        self.save_button.clicked.connect(self.save_contents)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_label.setText(f"Selected folder: {folder_path}")
            self.model.setRootPath(folder_path)
            self.tree.setRootIndex(self.model.index(folder_path))
            self.folder_path = folder_path
            self.tree.expandAll()

    def folder_clicked(self, index):
        file_path = self.model.filePath(index)
        if os.path.isdir(file_path):
            self.tree.setExpanded(index, not self.tree.isExpanded(index))
            self.tree.setSelection(self.tree.visualRect(index),
                                   QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
            self.tree.selectAll()

    def save_contents(self):
        indexes = self.tree.selectedIndexes()
        selected_paths = set([self.model.filePath(index) for index in indexes])  # keeping unique paths

        output_structure = self.process_directory(self.folder_path, selected_paths.copy())
        output_content = self.process_directory_content(selected_paths)

        with open("output.txt", 'w') as output_file:
            output_file.write(output_structure)
            output_file.write("\n")
            output_file.write(output_content)

    def process_directory(self, folder_path, selected_paths, indent=''):
        output = ''
        selected = folder_path in selected_paths
        if selected:
            output += f"{indent}>{os.path.basename(folder_path)}\n"
            selected_paths.remove(folder_path)

        for entry in os.scandir(folder_path):
            if entry.name == '.git':
                continue
            if entry.name == 'venv':
                continue
            if entry.name == '.idea':
                continue
            if entry.is_file():
                if entry.path in selected_paths or selected:
                    output += f"{indent} -{entry.name}\n"
                    selected_paths.discard(entry.path)
                else:
                    # output += f"{indent} -{entry.name}: Content not picked\n"
                    output += f"{indent} -{entry.name}\n"
            elif entry.is_dir():
                subdir_output = self.process_directory(entry.path, selected_paths, indent + ' ' * 2)
                if subdir_output:
                    output += f"{indent}>{entry.name}\n"
                    output += subdir_output
        return output

    def process_directory_content(self, selected_paths):
        output = ''
        for path in selected_paths:
            if os.path.isfile(path):
                output += f"{os.path.basename(path)}:\n"
                output += self.read_file(path)
                output += "\n\n"
        return output

    def read_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
        except:
            content = "(file content)"
        return content


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = FolderReader()
    window.show()

    sys.exit(app.exec_())
