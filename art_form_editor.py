import sys
import json_handler
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QTextEdit, QPushButton, QDialog, QDialogButtonBox, QLabel, QLineEdit, QMessageBox
from PySide6.QtCore import Qt

class ArtFormEditor(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize selected art form and its description
        self.selected_art_form = None

        # Set up the UI
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Art Form Editor")

        # Create layout and widgets
        layout = QVBoxLayout()

        # Dropdown menu for art forms
        self.art_form_dropdown = QComboBox()
        self.art_form_dropdown.addItems(self.load_art_forms())  # Load art forms from JSON
        self.art_form_dropdown.currentIndexChanged.connect(self.select_art_form)
        layout.addWidget(self.art_form_dropdown)

        # Editable description box
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Select an art form to edit")
        layout.addWidget(self.description_edit)

        # Save changes button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        layout.addWidget(self.save_button)

        # Remove art form button
        self.remove_button = QPushButton("Remove Art Form")
        self.remove_button.clicked.connect(self.remove_art_form)
        layout.addWidget(self.remove_button)

        # Add new art form button
        self.add_button = QPushButton("Add New Art Form")
        self.add_button.clicked.connect(self.add_new_art_form)
        layout.addWidget(self.add_button)

        # Set layout for the widget
        self.setLayout(layout)

    def load_art_forms(self):
        """Load art forms from the JSON file."""
        art_styles = json_handler.load_art_styles()
        return [art_style["name"] for art_style in art_styles]

    def select_art_form(self):
        """Load the description of the selected art form."""
        self.selected_art_form = self.art_form_dropdown.currentText()
        art_styles = json_handler.load_art_styles()
        for art_style in art_styles:
            if art_style["name"] == self.selected_art_form:
                self.description_edit.setText(art_style["description"])
                break

    def save_changes(self):
        """Save changes to the selected art form."""
        if self.selected_art_form:
            new_description = self.description_edit.toPlainText()
            json_handler.update_art_style(self.selected_art_form, new_description)
            QMessageBox.information(self, "Success", "Art form description updated successfully.")
        else:
            QMessageBox.warning(self, "No Selection", "Please select an art form to edit.")

    def remove_art_form(self):
        """Remove the selected art form from the JSON file."""
        if self.selected_art_form:
            json_handler.remove_art_style(self.selected_art_form)
            self.art_form_dropdown.clear()
            self.art_form_dropdown.addItems(self.load_art_forms())
            self.description_edit.clear()
            self.selected_art_form = None
            QMessageBox.information(self, "Success", "Art form removed successfully.")
        else:
            QMessageBox.warning(self, "No Selection", "Please select an art form to remove.")

    def add_new_art_form(self):
        """Open dialog to add a new art form."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Art Form")
        dialog.setModal(True)

        dialog_layout = QVBoxLayout()

        # Name input
        name_input = QLineEdit()
        name_input.setPlaceholderText("Art form name")
        dialog_layout.addWidget(name_input)

        # Description input
        description_input = QTextEdit()
        description_input.setPlaceholderText("Art form description")
        dialog_layout.addWidget(description_input)

        # Save button
        button_box = QDialogButtonBox(QDialogButtonBox.Save)
        button_box.accepted.connect(lambda: self.save_new_art_form(dialog, name_input.text(), description_input.toPlainText()))
        dialog_layout.addWidget(button_box)

        dialog.setLayout(dialog_layout)
        dialog.exec_()  # Show the dialog and wait for user interaction

    def save_new_art_form(self, dialog, name, description):
        """Save the new art form to the JSON file."""
        if name and description:
            json_handler.add_art_style(name, description)
            self.art_form_dropdown.addItem(name)
            dialog.accept()
            QMessageBox.information(self, "Success", "New art form added successfully.")
        else:
            QMessageBox.warning(self, "Invalid Input", "Please enter both name and description.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = ArtFormEditor()
    editor.show()
    sys.exit(app.exec())


