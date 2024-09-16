import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from photo_restyler import PhotoRestylerWindow
from art_form_editor import ArtFormEditor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Ensure all necessary directories and files exist
        self.ensure_directories_and_files()

        # Set up the main window
        self.setWindowTitle("Main Menu")
        self.setFixedWidth(400)

        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Create buttons for navigation
        self.photo_restyler_button = QPushButton("Open Photo Restyler")
        self.photo_restyler_button.clicked.connect(self.open_photo_restyler)
        layout.addWidget(self.photo_restyler_button)

        self.art_form_editor_button = QPushButton("Open Art Form Editor")
        self.art_form_editor_button.clicked.connect(self.open_art_form_editor)
        layout.addWidget(self.art_form_editor_button)

        # Set layout for central widget
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def ensure_directories_and_files(self):
        # Get the current working directory
        base_dir = os.getcwd()

        # Define necessary paths
        paths = {
            'image_restyle_description': 'image_restyle_description.txt',
            'json_handler': 'json_handler.py',
            'photo_restyler': 'photo_restyler.py',
            'art_form_editor': 'art_form_editor.py',
            'art_styles': 'art_styles.json',
            'photos': 'Photos'
        }

        # Ensure all directories exist
        if not os.path.exists(os.path.join(base_dir, paths['photos'])):
            os.makedirs(os.path.join(base_dir, paths['photos']))

        # Ensure all files exist
        for file_name in [paths['image_restyle_description'], paths['json_handler'], paths['photo_restyler'], paths['art_form_editor'], paths['art_styles']]:
            file_path = os.path.join(base_dir, file_name)
            if not os.path.isfile(file_path):
                with open(file_path, 'w') as f:
                    pass  # Create an empty file if it does not exist

    def open_photo_restyler(self):
        self.photo_restyler_window = PhotoRestylerWindow(self.show)  # Pass the method to show the main window
        self.photo_restyler_window.show()

    def open_art_form_editor(self):
        self.art_form_editor_window = ArtFormEditor()  # Use the correct class name
        self.art_form_editor_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
