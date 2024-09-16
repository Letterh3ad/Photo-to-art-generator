import sys
import json
import requests
import os
import shutil
import subprocess
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

        # Initialize variables
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
        art_styles = self.load_art_styles()
        for style in art_styles:
            self.art_style_dropdown.addItem(style['name'])  # Populate dropdown with art style names
        self.art_style_dropdown.currentIndexChanged.connect(self.select_art_style)
        layout.addWidget(self.art_style_dropdown)

        self.art_form_label = QLabel("Selected Art Style: {selected_art_style}")
        self.art_form_label.setWordWrap(True)
        layout.addWidget(self.art_form_label)

        self.edit_art_form_button = QPushButton("Edit Art Form")
        self.edit_art_form_button.setVisible(False)  # Initially hidden
        self.edit_art_form_button.clicked.connect(self.edit_art_form)
        layout.addWidget(self.edit_art_form_button)

        # Label to display the editable art style prompt
        self.prompt_label = QTextEdit("Art style prompt will appear here")
        self.prompt_label.setVisible(False)  # Hidden initially
        layout.addWidget(self.prompt_label)


        # Label to display the generated description
        self.generated_description_label = QTextEdit("Generated description will appear here")
        self.generated_description_label.setVisible(False)  # Hidden initially
        self.generated_description_label.setReadOnly(True)  # Make it read-only
        layout.addWidget(self.generated_description_label)

        # Progress bar to show the process of generating the description
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)  # Initial value of the progress bar
        self.progress_bar.setVisible(False)  # Hide initially
        layout.addWidget(self.progress_bar)

        # Label to display the current step of the progress
        self.step_label = QLabel("Step: Starting...")
        self.step_label.setVisible(False)  # Hide initially
        layout.addWidget(self.step_label)

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
        self.prompt_label.setVisible(not checked)
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
                return data
        except FileNotFoundError:
            print("The JSON file was not found.")
            return []
        except json.JSONDecodeError:
            print("Error decoding the JSON file.")
            return []

    def select_art_style(self):
        """Get the selected art style from the dropdown menu."""
        self.selected_art_style = self.art_style_dropdown.currentText()

        # Update the art form label
        self.art_form_label.setText(f"Selected Art Form: {self.selected_art_style}")

        # Fetch and display the prompt for the selected art style
        if self.selected_art_style != "Select Artform":
            self.update_prompt_for_art_style()

    def update_prompt_for_art_style(self):
        """Fetch and display the prompt for the selected art style."""
        art_styles = self.load_art_styles()

        # Find the prompt for the selected art style
        prompt = None
        for style in art_styles:
            if isinstance(style, dict) and style.get('name') == self.selected_art_style:
                prompt = style.get('description', '')  # Use description as prompt
                break

        if prompt:
            self.prompt_label.setText(prompt)
            self.prompt_label.setVisible(True)
        else:
            self.prompt_label.setText("Prompt not available.")
            self.prompt_label.setVisible(True)

    def select_image(self):
        """Open a file dialog to select an image."""
        image_file, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.bmp)")

        if image_file:
            self.selected_image_path = image_file

            # Check if the file exists
            if not os.path.isfile(self.selected_image_path):
                QMessageBox.warning(self, "Error", "The selected image file does not exist.")
                return

            # Display the selected image in the QLabel
            pixmap = QPixmap(self.selected_image_path)
            if pixmap.isNull():
                QMessageBox.warning(self, "Error", "Failed to load the image.")
                return

            self.image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))  # Scale the image to fit the label

            # Only proceed with description generation if enabled
            if self.description_generation_enabled:
                self.progress_bar.setVisible(True)
                self.step_label.setVisible(True)
                self.Img_Description()
        else:
            QMessageBox.warning(self, "No Image", "Please select an image file.")

    def Img_Description(self):
        """Generate a description for the selected image."""
        try:
            if not self.description_generation_enabled:
                return  # Exit if description generation is disabled

            self.progress_bar.setValue(20)
            self.step_label.setText("Step: Launching browser")
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)

                self.progress_bar.setValue(40)
                self.step_label.setText("Step: Navigating to website")
                page = browser.new_page()
                page.goto("https://imagedescriptiongenerator.net/")

                self.progress_bar.setValue(60)
                self.step_label.setText("Step: Uploading image")
                page.set_input_files('input[type="file"]', self.selected_image_path)

                page.wait_for_timeout(2000)  # Wait for the upload to complete
                page.click('button:has-text("Generate Description")')

                self.progress_bar.setValue(80)
                self.step_label.setText("Step: Generating description")
                page.wait_for_selector('#GenDescription')

                self.generated_description = page.inner_text('#GenDescription')
                self.progress_bar.setValue(90)
                self.step_label.setText("Step: Description generated")

                # Write description to the fixed file
                with open(self.description_file_path, 'w') as file:
                    file.write(self.generated_description)

                self.progress_bar.setValue(100)
                self.step_label.setText("Step: Description saved")
                browser.close()

                # Display the generated description
                self.generated_description_label.setText(self.generated_description)
                self.generated_description_label.setVisible(True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred during description generation: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
            self.step_label.setVisible(False)

    def edit_description(self):
        """Edit the description in a dialog box."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Description")
        layout = QVBoxLayout()

        description_edit = QTextEdit()
        description_edit.setText(self.generated_description)
        layout.addWidget(description_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.save_description(description_edit.toPlainText()))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec()

    def save_description(self, new_description):
        """
        Save the edited description to the file. If the 'Hand Drawn' style is selected,
        a brief prompt will be saved into image_restyle_description.txt.
        """
        try:
            # If 'Hand Drawn' is the selected style, override with a specific prompt
            if self.selected_art_style == 'Hand Drawn':
                new_description = "Transform the image into a hand-drawn artistic style with visible strokes and texture."

            # Save the description to the description file path
            with open(self.description_file_path, 'w') as file:
                file.write(new_description)
            
            # Update the stored description and the UI label
            self.generated_description = new_description
            self.generated_description_label.setText(new_description)
            
            print(f"Description saved successfully: {new_description}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while saving the description: {str(e)}")


    def restyle_img(self):
        """Handle the image restyling and clarity enhancement process."""
        if self.restyle_in_progress:
            QMessageBox.warning(self, "Process In Progress", "Restyling is already in progress.")
            return
        
        self.restyle_in_progress = True
        self.progress_bar.setValue(10)
        self.progress_bar.setVisible(True)
        self.step_label.setVisible(True)
        self.step_label.setText("Step: Starting restyling")

        # Check if image and art style are selected
        if not self.selected_image_path:
            QMessageBox.warning(self, "No Image", "Please select an image file.")
            self.restyle_in_progress = False
            self.progress_bar.setVisible(False)
            self.step_label.setVisible(False)
            return

        if not self.selected_art_style or self.selected_art_style == "Select Artform":
            QMessageBox.warning(self, "No Art Style", "Please select an art style.")
            self.restyle_in_progress = False
            self.progress_bar.setVisible(False)
            self.step_label.setVisible(False)
            return

        # Write the prompt to the fixed file
        with open(self.description_file_path, 'w') as file:
            file.write(self.prompt_label.toPlainText())

        if self.select_art_style == "Hand Drawn":
            # Call the function to handle hand drawn style
            self.restyle_with_subprocess(self.selected_image)
        else:
        
            self.progress_bar.setValue(30)
            self.step_label.setText("Step: Sending request to DeepAI for restyling")

            # Prepare files for API request
            image_file = open(self.selected_image_path, 'rb')
            description_file = open(self.description_file_path, 'rb')

            # Print file paths and contents for debugging
            print(f"Image file path: {self.selected_image_path}")
            print(f"Description file path: {self.description_file_path}")
            
            # Read and print contents of files
            image_file_contents = image_file.read()
            description_file_contents = description_file.read()

            # Ensure files are properly closed after reading
            image_file.seek(0)  # Reset file pointer to beginning
            description_file.seek(0)  # Reset file pointer to beginning
            
            print("Image file contents (first 100 bytes):", image_file_contents[:100])
            print("Description file contents:", description_file_contents.decode('utf-8'))

            # Close files
            image_file.close()
            description_file.close()

            # Send request to DeepAI for restyling
            try:
                response = requests.post(
                    "https://api.deepai.org/api/image-editor",
                    files={
                        'image': open(self.selected_image_path, 'rb'),
                        'text': open(self.description_file_path, 'rb'),
                    },
                    headers={'api-key': self.api_key}
                )
                self.progress_bar.setValue(70)
                self.step_label.setText("Step: Processing response")

                if response.status_code == 200:
                    response_data = response.json()
                    if 'output_url' in response_data:
                        # Save restyled image before clarity enhancement
                        restyled_image_url = response_data['output_url']
                        self.restyled_image_path = self.download_image(restyled_image_url, 'restyled_image.jpg')

                        self.progress_bar.setValue(80)
                        self.step_label.setText("Step: Enhancing image clarity")

                        # Enhance clarity using the Torch SRGAN API
                        clarity_response = requests.post(
                            "https://api.deepai.org/api/waifu2x",
                            files={
                                'image': open(self.restyled_image_path, 'rb'),
                            },
                            headers={'api-key': self.api_key}
                        )
                        
                        if clarity_response.status_code == 200:
                            clarity_data = clarity_response.json()
                            if 'output_url' in clarity_data:
                                clarity_image_url = clarity_data['output_url']
                                self.enhanced_image_path = self.download_image(clarity_image_url, 'enhanced_image.jpg')

                                self.progress_bar.setValue(90)
                                self.step_label.setText("Step: Downloading enhanced image")

                                pixmap = QPixmap(self.enhanced_image_path)
                                self.edited_image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
                                self.save_button.setVisible(True)

                            else:
                                QMessageBox.warning(self, "Error", "No output URL found in the clarity response.")
                        else:
                            QMessageBox.warning(self, "Error", f"Failed to enhance image clarity: {clarity_response.status_code}")

                    else:
                        QMessageBox.warning(self, "Error", "No output URL found in the restyling response.")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to restyle the image: {response.status_code}")

            except requests.RequestException as e:
                QMessageBox.warning(self, "Error", f"An error occurred while sending the request: {str(e)}")
            finally:
                self.restyle_in_progress = False
                self.progress_bar.setVisible(False)
                self.step_label.setVisible(False)

    def restyle_with_subprocess(self, image_path, text_path):
        """
        Function to handle the "Hand Drawn" style using subprocess to run the external script.
        """
        hand_drawn_script_path = os.path.join(os.getcwd(), 'restyle_pipelines', 'hand_drawn.py')
        
        try:
            # Run the external script via subprocess, passing the image and text paths
            subprocess.run(['python', hand_drawn_script_path, image_path, text_path], check=True)
            print("Successfully restyled the image using the Hand Drawn style.")
        except subprocess.CalledProcessError as e:
            print(f"Error running the hand drawn script: {e}")

    def download_image(self, image_url, filename):
        """Download an image from the provided URL and save it with the given filename."""
        response = requests.get(image_url)
        response.raise_for_status()  # Ensure we got a successful response
        image_path = filename
        with open(image_path, 'wb') as file:
            file.write(response.content)
        return image_path


    def save_edited_image(self):
        """Save the edited image to a file."""
        if self.edited_image_path:
            save_file, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Image Files (*.jpg *.png)")
            if save_file:
                shutil.copy(self.edited_image_path, save_file)
        else:
            QMessageBox.warning(self, "No Image", "No edited image to save.")

    def edit_art_form(self):
        """Edit the art form in a dialog box."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Art Form Prompt")
        layout = QVBoxLayout()

        prompt_edit = QTextEdit()
        prompt_edit.setText(self.prompt_label.toPlainText())
        layout.addWidget(prompt_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.save_art_form_prompt(prompt_edit.toPlainText()))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec()

    def save_art_form_prompt(self, new_prompt):
        """Save the edited art form prompt."""
        self.prompt_label.setText(new_prompt)
        with open(self.description_file_path, 'w') as file:
            file.write(new_prompt)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotoRestylerWindow(lambda: print("Back to main screen"))  # Dummy function for navigation
    window.show()
    sys.exit(app.exec())
