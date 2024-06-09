import os
import shutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QFrame, QDialog, QSizePolicy, QGridLayout)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from qt_material import apply_stylesheet

folder_path = "analysed/cropped"

class ImageAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set up the main window
        self.setWindowTitle('Image Analysis Display')
        self.setGeometry(100, 100, 1200, 800)

        # Define a common font size
        self.font_size = 12

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Main page
        self.main_page = QWidget()
        self.main_page_layout = QVBoxLayout()
        self.main_page.setLayout(self.main_page_layout)
        self.stacked_widget.addWidget(self.main_page)

        # Create and style the header label
        header_label = QLabel("L.I.S.A. Lightweight Intelligent Search Assistant")
        header_label.setFont(QFont("Helvetica", 10, QFont.Bold))  # Set font size and style for header
        header_label.setAlignment(Qt.AlignCenter)  # Center align the text

        self.main_page_layout.addWidget(header_label)  # Add header label to the main layout

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(30, 20, 30, 15)  # Left, Top, Right, Bottom margins

        # Create refresh button and connect it to refresh_table method
        refresh_button = QPushButton('Refresh', self)
        refresh_button.setFont(QFont("Helvetica", self.font_size))  # Use common font size
        refresh_button.clicked.connect(self.refresh_table)
        button_layout.addWidget(refresh_button)

        # Create reset button and connect it to confirm_reset_folder method
        reset_button = QPushButton('Reset Folder', self)
        reset_button.setFont(QFont("Helvetica", self.font_size))  # Use common font size
        reset_button.clicked.connect(self.confirm_reset_folder)
        button_layout.addWidget(reset_button)

        # Create analysis page button
        analysis_button = QPushButton('Image Analysis Image Specific', self)
        analysis_button.setFont(QFont("Helvetica", self.font_size))  # Use common font size
        analysis_button.clicked.connect(self.show_analysis_page)
        button_layout.addWidget(analysis_button)



        # Create scroll area for content
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.main_page_layout.addWidget(self.scroll_area)

        # Create content widget and layout
        self.content_widget = QWidget()
        self.scroll_area.setWidget(self.content_widget)
        self.content_layout = QVBoxLayout(self.content_widget)

        # Analysis page
        self.analysis_page = QWidget()
        self.analysis_page_layout = QVBoxLayout()
        self.analysis_page.setLayout(self.analysis_page_layout)
        self.stacked_widget.addWidget(self.analysis_page)

        # Specific image display page
        self.image_page = QWidget()
        self.image_page_layout = QHBoxLayout()
        self.image_page.setLayout(self.image_page_layout)
        self.stacked_widget.addWidget(self.image_page)

        # Add button layout to main layout
        self.main_page_layout.addLayout(button_layout)

        # Initial display of the table
        self.refresh_table()

    def show_analysis_page(self):
        self.analysis_page_layout.addWidget(QLabel("Select an Image"))
        images = [img for img in os.listdir("analysed") if img.endswith(".jpg")]
        for img in images:
            btn = QPushButton(img, self)
            btn.setFont(QFont("Helvetica", self.font_size))
            btn.clicked.connect(lambda ch, img=img: self.show_image_page(img))
            self.analysis_page_layout.addWidget(btn)

        # Back button to return to the main page
        back_button = QPushButton("Back", self)
        back_button.setFont(QFont("Helvetica", self.font_size))
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_page))
        self.analysis_page_layout.addWidget(back_button)

        self.stacked_widget.setCurrentWidget(self.analysis_page)



    def show_image_page(self, img):
        # Clear the layout before adding new widgets
        for i in reversed(range(self.image_page_layout.count())):
            widget = self.image_page_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Left side: Display the analyzed image
        analyzed_image_path = os.path.join("analysed", img)
        analyzed_image_label = QLabel()
        pixmap = QPixmap(analyzed_image_path)
        analyzed_image_label.setPixmap(pixmap.scaledToWidth(self.width() // 2))
        analyzed_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_page_layout.addWidget(analyzed_image_label)

        # Right side setup
        related_images_scroll_area = QScrollArea()
        related_images_scroll_area.setWidgetResizable(True)
        related_content_widget = QWidget()
        related_images_layout = QVBoxLayout(related_content_widget)
        related_images_scroll_area.setWidget(related_content_widget)
        self.image_page_layout.addWidget(related_images_scroll_area)

        # Load and display related cropped images and their details
        base_name = os.path.splitext(img)[0]
        print("base_name",base_name[9:])
        print("all files")
        for f in os.listdir(folder_path):
            print(f)
        related_images = [f for f in os.listdir(folder_path) if base_name[9:] in f and f.endswith('.jpg')]
        
        print(f"Related images found: {related_images}")  # Debugging print

        if not related_images:
            print("No related images found.")  # Check if the list is empty

        print("Finding TXT")
        for related_img in related_images:
            try:
                if related_img.endswith('.jpg'):
                    text_file = related_img[:-4] + ".txt"  # Correct way to replace '.jpg' with '.txt'
                    text_path = os.path.join(folder_path, text_file)
                    print(text_path)
                    if os.path.exists(text_path):
                        with open(text_path, 'r') as f:
                            content = f.read()
                        # Extract information from content
                        description = content.split('Description: ')[1].split('\nThreat:')[0].strip()
                        threat = content.split('Threat: ')[1].split('\nRating:')[0].strip()
                        rating = content.split('Rating: ')[1].split('/')[0].strip().strip('[]')
                        recommendation = content.split('Recommendation: ')[1].strip()
                        image_path = os.path.join(folder_path, related_img)
                        # Create and add the data entry frame
                        entry_frame = self.create_data_entry(image_path, description, threat, recommendation, rating)
                        related_images_layout.addWidget(entry_frame)
                        print(f"Added frame for: {related_img}")  # Confirm frame addition
                    else:
                        print(f"Text file not found for: {related_img}")  # Debug missing text files
            except:
                print("Error displaying:",related_img)
                continue

        self.stacked_widget.setCurrentWidget(self.image_page)


    def load_data(self):
        # Load data from text files and corresponding images
        data = []
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                with open(os.path.join(folder_path, filename), 'r') as f:
                    content = f.read()
                image_name = filename.replace('.txt', '.jpg')
                image_path = os.path.join(folder_path, image_name)

                try:
                    # Extract relevant data from the text file
                    description = content.split('Description: ')[1].split('\nThreat:')[0].strip()
                    threat = content.split('Threat: ')[1].split('\nRating:')[0].strip()
                    rating_str = content.split('Rating: ')[1].split('/')[0].strip().strip('[]')
                    rating = float(rating_str) if rating_str.isdigit() else 0
                    recommendation = content.split('Recommendation: ')[1].strip()

                    # Append extracted data to the data list
                    data.append((image_path, description, threat, recommendation, rating))
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    continue  # Skip if data is incorrectly formatted

        # Sort data by rating in descending order
        data.sort(key=lambda x: x[4], reverse=True)
        return data
    

    def confirm_reset_folder(self):
        # Confirm reset folder action with a dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm Reset")
        dialog_layout = QVBoxLayout()

        message = QLabel("Are you sure you want to reset the folder? This action cannot be undone.")
        message.setFont(QFont("Helvetica", self.font_size))  # Use common font size
        dialog_layout.addWidget(message)

        button_layout = QHBoxLayout()

        # Confirm button to reset folder
        confirm_button = QPushButton("Confirm")
        confirm_button.setFont(QFont("Helvetica", self.font_size))  # Use common font size
        confirm_button.clicked.connect(lambda: [self.reset_folder(), dialog.accept()])
        button_layout.addWidget(confirm_button)

        # Cancel button to close the dialog
        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(QFont("Helvetica", self.font_size))  # Use common font size
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        dialog_layout.addLayout(button_layout)
        dialog.setLayout(dialog_layout)
        dialog.exec_()

    def reset_folder(self):
        # Reset the 'analysed' folder by deleting its contents and recreating 'cropped' folder
        analysed_path = "analysed"
        cropped_path = os.path.join(analysed_path, "cropped")

        # Delete all files and folders in 'analysed' directory
        for filename in os.listdir(analysed_path):
            file_path = os.path.join(analysed_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

        # Recreate 'cropped' folder
        if not os.path.exists(cropped_path):
            try:
                os.makedirs(cropped_path)
            except Exception as e:
                print(f'Failed to create {cropped_path}. Reason: {e}')
        
        # Refresh the table after reset
        self.refresh_table()

    def create_data_entry(self, image_path, description, threat, recommendation, rating):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setLineWidth(1)
        frame.setStyleSheet("QFrame { border-radius: 10px; background-color: #333; margin: 10px; padding: 10px; }")

        layout = QGridLayout()

        # Create image label with fixed size and background color
        image_label = QLabel()
        image_label.setFixedSize(400, 400)  # Increased size to 400x400
        pixmap = QPixmap(image_path)
        if pixmap.width() > pixmap.height():
            pixmap = pixmap.scaledToHeight(400, Qt.SmoothTransformation)
        else:
            pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                
        image_label.setPixmap(pixmap)
        image_label.setStyleSheet("background-color: #222; border: 1px solid #555;")
        layout.addWidget(image_label, 0, 0, 4, 1)  # Image occupies 4 rows in the first column

        # Add text labels for description, threat, recommendation, and rating
        self.add_text_with_label(layout, "Description:", description, 0, 1)
        self.add_text_with_label(layout, "Threat:", threat, 1, 1)
        self.add_text_with_label(layout, "Recommendation:", recommendation, 2, 1)
        self.add_rating_with_label(layout, "Rating:", f"{rating}/10", 3, 1)

        frame.setLayout(layout)
        return frame

    def refresh_table(self):
        # Load data and refresh the display table
        data = self.load_data()
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        for image_path, description, threat, recommendation, rating in data:
            entry_frame = self.create_data_entry(image_path, description, threat, recommendation, rating)
            self.content_layout.addWidget(entry_frame)


    def add_text_with_label(self, layout, label_text, text_content, row, col):
        # Create and style the label for the text
        label = QLabel(label_text)
        label.setStyleSheet("QLabel { color: #FFF; }")
        label.setFont(QFont("Helvetica", self.font_size, QFont.Bold))  # Use common font size
        label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        layout.addWidget(label, row, col)

        # Create and style the text content
        text = QLabel(text_content)
        text.setStyleSheet("QLabel { color: #FFF; }")
        text.setWordWrap(True)
        text.setFont(QFont("Helvetica", self.font_size))  # Use common font size
        text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(text, row, col + 1)

    def add_rating_with_label(self, layout, label_text, rating_text, row, col):
        # Create and style the label for the rating
        label = QLabel(label_text)
        label.setStyleSheet("QLabel { color: #FFF; }")
        label.setFont(QFont("Helvetica", self.font_size, QFont.Bold))  # Use common font size
        label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        layout.addWidget(label, row, col)

        # Create and style the rating text
        rating_label = QLabel(rating_text)
        rating_label.setStyleSheet("QLabel { color: #FFF; }")
        rating_label.setFont(QFont("Helvetica", self.font_size))  # Use common font size
        layout.addWidget(rating_label, row, col + 1)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_cyan.xml')
    ex = ImageAnalysisApp()
    ex.show()
    sys.exit(app.exec_())
