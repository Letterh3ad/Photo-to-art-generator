import sys
import json
import requests
import os
import shutil
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, 
    QMessageBox, QProgressBar, QTextEdit, QDialog, QDialogButtonBox, QComboBox, 
    QCheckBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from playwright.sync_api import sync_playwright

class PhotoRestylerWindow(QWidget):
    def __init__(self, go_to_main):
        super().__init__()
        self.go_to_main = go_to_main  # Function to navigate back to the main screen

        # Initialize the variable to store the image path, description, and selected art style
        self.selected_image_path = None
        self.generated_description = None
        self.selected_art_style = None
        self.edited_image_path = None
        self.description_generation_enabled = False
        self.description_file_path = 'image_restyle_description.txt'  # Fixed file path
        self.restyle_in_progress = False

        # Load DeepAI API key
        self.api_key = self.load_deepai_key()

        # Set up the UI
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Photo Restyler")

        # Set fixed width and allow height to stretch
        self.setFixedWidth(800)  # Set a fixed width

        # Create layout and widgets
        layout = QVBoxLayout()

        # Image display label
        self.image_label = QLabel("No image selected")
        layout.addWidget(self.image_label)

        # Select image button
        self.button = QPushButton("Select Image")
        self.button.clicked.connect(self.select_image)
        layout.addWidget(self.button)

        # Toggle box for description generation
        self.desc_gen_toggle = QCheckBox("Enable Description Generation")
        self.desc_gen_toggle.setChecked(False)  # Start turned off
        self.desc_gen_toggle.toggled.connect(self.toggle_description_generation)
        layout.addWidget(self.desc_gen_toggle)

        # Dropdown menu for art styles
        self.art_style_dropdown = QComboBox()
        self.art_style_dropdown.addItem("Select Artform")
        self.art_style_dropdown.addItems(self.load_art_styles())  # Load art styles from JSON
        self.art_style_dropdown.currentIndexChanged.connect(self.select_art_style)
        layout.addWidget(self.art_style_dropdown)
        
        self.art_form_label = QLabel("Selected Art Form: None")
        self.art_form_label.setWordWrap(True)

        self.edit_art_form_button = QPushButton("Edit Art Form")
        self.edit_art_form_button.setVisible(False)  # Initially hidden
        self.edit_art_form_button.clicked.connect(self.edit_art_form)
    
        # Label to display the generated description
        self.description_label = QLabel("Generated description will appear here")
        self.description_label.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.description_label.setWordWrap(True)  # Allow the text to wrap
        self.description_label.setVisible(False)  # Hidden initially
        layout.addWidget(self.description_label)

        # Progress bar to show the process of generating the description
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)  # Initial value of the progress bar
        self.progress_bar.setVisible(False)  # Hide initially
        layout.addWidget(self.progress_bar)

        # Label to display the current step of the progress
        self.step_label = QLabel("Step: Starting...")
        self.step_label.setVisible(False)  # Hide initially
        layout.addWidget(self.step_label)

        # Button to edit the description (hidden by default)
        self.edit_button = QPushButton("Edit Description")
        self.edit_button.setVisible(False)  # Hidden initially
        self.edit_button.clicked.connect(self.edit_description)
        layout.addWidget(self.edit_button)

        # Button to restyle the image
        self.restyle_button = QPushButton("Restyle Image")
        self.restyle_button.clicked.connect(self.restyle_img)
        layout.addWidget(self.restyle_button)

        # Button to save the edited image
        self.save_button = QPushButton("Save Edited Image")
        self.save_button.setVisible(False)  # Hidden initially
        self.save_button.clicked.connect(self.save_edited_image)
        layout.addWidget(self.save_button)

        # Label to display the edited image
        self.edited_image_label = QLabel("Edited image will appear here")
        layout.addWidget(self.edited_image_label)

        # Set layout for the widget
        self.setLayout(layout)

    def load_deepai_key(self):
        """Load DeepAI API key from storage.txt."""
        try:
            with open('storage.txt', 'r') as file:
                for line in file:
                    if line.startswith('deepai-key:'):
                        return line.split(':')[1].strip()
        except FileNotFoundError:
            print("The storage.txt file was not found.")
        except Exception as e:
            print(f"An error occurred while reading the API key: {str(e)}")
        return None

    def toggle_description_generation(self, checked):
        self.description_generation_enabled = checked
        self.description_label.setVisible(checked)
        if not checked:
            # Hide progress bar and step label if description generation is disabled
            self.progress_bar.setVisible(False)
            self.step_label.setVisible(False)
        else:
            self.progress_bar.setVisible(True)
            self.step_label.setVisible(True)

    def load_art_styles(self):
        """Load art styles from the JSON file."""
        try:
            with open('art_styles.json', 'r') as file:
                data = json.load(file)
                return [style['name'] for style in data]
        except FileNotFoundError:
            print("The JSON file was not found.")
            return []
        except json.JSONDecodeError:
            print("Error decoding the JSON file.")
            return []

    def select_art_style(self):
        """Get the selected art style from the dropdown menu."""
        self.selected_art_style = self.art_style_dropdown.currentText()

    def select_image(self):
        """Open a file dialog to select an image."""
        image_file, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.bmp)")

        # Store the selected image path in the variable
        if image_file:
            self.selected_image_path = image_file

            # Display the selected image in the QLabel
            pixmap = QPixmap(self.selected_image_path)
            self.image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))  # Scale the image to fit the label

            # Only proceed with description generation if enabled
            if self.description_generation_enabled:
                # Show the progress bar and step label
                self.progress_bar.setVisible(True)
                self.step_label.setVisible(True)

                # Call the Img_Description() function to generate the description
                self.Img_Description()
        else:
            # Show an error message if no image was selected
            QMessageBox.warning(self, "No Image", "Please select an image file.")

    def on_art_form_selected(self, index):
        """Handle the selection of an art form from the dropdown menu."""
        art_form = self.art_form_dropdown.currentText()
        if art_form:
            self.art_form_label.setText(f"Selected Art Form: {art_form}")
            self.edit_art_form_button.setVisible(True)  # Show the edit button
        else:
            self.art_form_label.setText("Selected Art Form: None")
            self.edit_art_form_button.setVisible(False)  # Hide the edit button

    def Img_Description(self):
        """Generate a description for the selected image."""
        try:
            if not self.description_generation_enabled:
                return  # Exit if description generation is disabled

            # Step 1: Launch Playwright
            self.progress_bar.setValue(20)
            self.step_label.setText("Step: Launching browser")
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)

                # Step 2: Open new page and navigate to the image description generator website
                self.progress_bar.setValue(40)
                self.step_label.setText("Step: Navigating to website")
                page = browser.new_page()
                page.goto("https://imagedescriptiongenerator.net/")

                # Step 3: Upload the image
                self.progress_bar.setValue(60)
                self.step_label.setText("Step: Uploading image")
                page.set_input_files('input[type="file"]', self.selected_image_path)

                # Wait for the image to be uploaded and click the "Generate Description" button
                page.wait_for_timeout(2000)  # Wait for the upload to complete
                page.click('button:has-text("Generate Description")')

                # Step 4: Wait for the description element with id="GenDescription" to appear
                self.progress_bar.setValue(80)
                self.step_label.setText("Step: Generating description")
                page.wait_for_selector('#GenDescription')

                # Step 5: Retrieve the generated description
                self.generated_description = page.inner_text('#GenDescription')
                self.progress_bar.setValue(90)
                self.step_label.setText("Step: Retrieving description")

                # Show the description in the QLabel below the image
                self.description_label.setText(f"Generated Description:\n{self.generated_description}")
                self.description_label.adjustSize()

                # Step 6: Close the browser
                self.progress_bar.setValue(100)
                self.step_label.setText("Step: Closing browser")
                browser.close()

                # Show the Edit Description button
                self.progress_bar.setVisible(False)
                self.step_label.setVisible(False)
                self.edit_button.setVisible(True)

        except Exception as e:
            # Show an error message if something goes wrong
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            # Reset progress bar in case of error
            self.progress_bar.setValue(0)
            self.step_label.setText("Step: Error occurred")

    def restyle_img(self):
        """Restyle the selected image based on the chosen art style."""
        if self.restyle_in_progress:
            QMessageBox.warning(self, "In Progress", "Restyling is already in progress. Please wait.")
            return

        if not self.selected_image_path:
            QMessageBox.warning(self, "No Image", "Please select an image first.")
            return

        if not self.selected_art_style:
            QMessageBox.warning(self, "No Art Style", "Please select an art style.")
            return

        self.restyle_in_progress = True
        self.restyle_button.setEnabled(False)  # Disable the button to prevent multiple requests

        # Update UI to show progress
        self.progress_bar.setValue(10)
        self.step_label.setText("Step: Preparing description")
        self.progress_bar.setVisible(True)
        self.step_label.setVisible(True)

        try:
            # Load the description for the selected art style
            art_styles = self.load_art_styles_from_file()
            art_style_description = next((style['description'] for style in art_styles if style['name'] == self.selected_art_style), "")

            if not art_style_description:
                QMessageBox.warning(self, "Error", "Description for the selected art style not found.")
                self.restyle_in_progress = False
                self.restyle_button.setEnabled(True)
                return

            # Prepare the files for the API request
            api_url = "https://api.deepai.org/api/image-editor"
            headers = {
                'api-key': self.api_key
            }
            files = {
                'image': open(self.selected_image_path, 'rb'),
                'text': ('description.txt', art_style_description)
            }

            self.progress_bar.setValue(20)
            self.step_label.setText("Step: Sending request")

            # Send the request to the API
            response = requests.post(api_url, headers=headers, files=files)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Handle the response
            response_data = response.json()
            if 'output_url' in response_data:
                output_url = response_data['output_url']

                # Download and save the edited image
                self.progress_bar.setValue(60)
                self.step_label.setText("Step: Downloading edited image")
                response = requests.get(output_url, stream=True)
                with open('edited_image.png', 'wb') as f:
                    shutil.copyfileobj(response.raw, f)

                # Update the UI with the edited image
                self.edited_image_path = 'edited_image.png'
                pixmap = QPixmap(self.edited_image_path)
                self.edited_image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))  # Scale the image to fit the label
                self.edited_image_label.setText("Edited image:")
                self.save_button.setVisible(True)  # Show the save button

                QMessageBox.information(self, "Success", "Image has been restyled successfully.")
                self.progress_bar.setValue(100)
                self.step_label.setText("Step: Completed")
            else:
                QMessageBox.warning(self, "Error", "Failed to retrieve the restyled image from the API response.")

        except requests.RequestException as e:
            QMessageBox.critical(self, "API Error", f"An error occurred while contacting the API: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
        finally:
            self.restyle_in_progress = False
            self.restyle_button.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.step_label.setVisible(False)

    def load_art_styles_from_file(self):
        """Load art styles and their descriptions from the JSON file."""
        try:
            with open('art_styles.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print("The JSON file was not found.")
            return []
        except json.JSONDecodeError:
            print("Error decoding the JSON file.")
            return []

    def edit_art_form(self):
        """Allow the user to edit the selected art form and update the JSON file."""
        current_art_form = self.art_form_dropdown.currentText()

        # Get the new name for the art form
        new_name, ok = QInputDialog.getText(self, "Edit Art Form Name", "Enter new name for the art form:", QLineEdit.Normal, current_art_form)
        
        if ok and new_name:
            # Get the current art form description
            art_styles = load_art_styles()
            current_art_style = next((style for style in art_styles if style["name"] == current_art_form), None)

            if current_art_style:
                # Show a dialog to edit the description
                dialog = QDialog(self)
                dialog.setWindowTitle("Edit Art Form Description")
                dialog_layout = QVBoxLayout()

                text_edit = QTextEdit(dialog)
                text_edit.setText(current_art_style["description"])
                dialog_layout.addWidget(text_edit)

                button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, dialog)
                button_box.accepted.connect(lambda: self.save_art_form(new_name, text_edit.toPlainText(), current_art_form))
                button_box.rejected.connect(dialog.reject)
                dialog_layout.addWidget(button_box)

                dialog.setLayout(dialog_layout)
                dialog.exec()

    def save_art_form(self, new_name, new_description, old_name):
        """Save the edited art form to the JSON file."""
        # Update the art form in the JSON file
        if old_name != new_name:
            # Remove old art form
            remove_art_style(old_name)

            # Add new art form
            add_art_style(new_name, new_description)
        else:
            # Update the art form description
            update_art_style(new_name, new_description)

        # Update the dropdown menu
        self.art_form_dropdown.clear()
        self.art_form_dropdown.addItems([style['name'] for style in load_art_styles()])

        # Set the updated art form in the label
        self.art_form_label.setText(f"Selected Art Form: {new_name}")
        self.edit_art_form_button.setVisible(True)  # Show the edit button

    def restyle_image_with_deepai(self, description):
        """
        Restyle the image using the DeepAI API with the provided description.
        """
        api_url = "https://api.deepai.org/api/text2img"
        headers = {"Api-Key": "YOUR_DEEPAI_API_KEY"}
        with open(self.selected_image_path, 'rb') as image_file:
            response = requests.post(api_url, headers=headers, files={'image': image_file}, data={'text': description})
            response.raise_for_status()  # Raise an error for HTTP errors
            response_data = response.json()
            image_url = response_data.get('output', {}).get('url', None)
            if image_url:
                # Download the edited image
                edited_image_response = requests.get(image_url, stream=True)
                edited_image_response.raise_for_status()
                edited_image_path = 'edited_image.png'
                with open(edited_image_path, 'wb') as f:
                    shutil.copyfileobj(edited_image_response.raw, f)
                return edited_image_path
            return None

    def save_edited_image(self):
        if not self.edited_image_path:
            QMessageBox.warning(self, "No Image", "No edited image available to save.")
            return

        # Open a file dialog to select the save location
        save_file, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Image Files (*.png *.jpg *.bmp)")
        if save_file:
            shutil.copy(self.edited_image_path, save_file)
            QMessageBox.information(self, "Image Saved", "The edited image has been saved successfully.")

    def edit_description(self):
        if self.generated_description:
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Description")

            # Layout and widgets for editing the description
            dialog_layout = QVBoxLayout()
            text_edit = QTextEdit(dialog)
            text_edit.setText(self.generated_description)
            dialog_layout.addWidget(text_edit)

            button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, dialog)
            button_box.accepted.connect(lambda: self.save_description(text_edit.toPlainText()))
            button_box.rejected.connect(dialog.reject)
            dialog_layout.addWidget(button_box)

            dialog.setLayout(dialog_layout)
            dialog.exec()

    def save_description(self, new_description):
        self.generated_description = new_description
        with open(self.description_file_path, 'w') as file:
            file.write(new_description)
        self.description_label.setText(f"Updated Description:\n{new_description}")
