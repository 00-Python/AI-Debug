import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QVBoxLayout, QPushButton, QLabel, QFileSystemModel
from PyQt5.QtCore import Qt

class DirectoryBrowser(QWidget):
    def __init__(self, title):
        super().__init__()

        self.setWindowTitle(title)
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.tree_view = QTreeView()
        self.tree_view.setSelectionMode(QTreeView.MultiSelection)
        self.model = QFileSystemModel()
        current_directory = os.getcwd()
        self.model.setRootPath(current_directory)

        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(current_directory))

        self.selected_items = []

        self.select_button = QPushButton("Select")
        self.select_button.clicked.connect(self.get_selected_items)

        self.layout.addWidget(self.tree_view)
        self.layout.addWidget(self.select_button)

        self.setLayout(self.layout)
        
    def get_selected_items(self):
        selected_indexes = self.tree_view.selectionModel().selectedIndexes()
        selected_items = [self.model.filePath(index) for index in selected_indexes]

        # Recursively add subfiles and subdirectories
        recursive_selected_items = self.recursive_selection(selected_items)

        self.selected_items = list(set(recursive_selected_items))  # Filter out duplicates
        # self.selected_items_label.setText("Selected items:\n" + "\n".join(self.selected_items))
        self.close()  # Close the GUI

    def recursive_selection(self, paths):
        selected_items = []
        for path in paths:
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    selected_items.extend([os.path.join(root, f) for f in files])
                    selected_items.extend([os.path.join(root, d) for d in dirs])
            else:
                selected_items.append(path)
        return selected_items

def main(tab_name):
    app = QApplication(sys.argv)
    window = DirectoryBrowser(tab_name)
    window.show()
    app.exec_()
    # Return selected_items from the DirectoryBrowser instance
    return window.selected_items

if __name__ == "__main__":
    selected_items = main("Your Tab Name")
    print("Selected Items:", selected_items)
