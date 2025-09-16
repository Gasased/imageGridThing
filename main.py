import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QWidget,
    QLabel,
    QScrollArea,
    QVBoxLayout,
)
from PyQt5.QtGui import QPixmap, QKeyEvent, QResizeEvent
from PyQt5.QtCore import Qt

# --- Dark Theme Stylesheet ---
dark_stylesheet = """
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        font-family: Segoe UI;
        font-size: 10pt;
    }
    QMainWindow {
        background-color: #2b2b2b;
    }
    QLabel a {
        color: #3399ff;
        text-decoration: none;
    }
    QLabel a:hover {
        text-decoration: underline;
    }
    QScrollArea {
        border: none;
    }
    /* Style for the scrollbars */
    QScrollBar:vertical {
        border: none;
        background: #3c3c3c;
        width: 14px;
        margin: 15px 0 15px 0;
        border-radius: 7px;
    }
    QScrollBar::handle:vertical {
        background-color: #5a5a5a;
        min-height: 30px;
        border-radius: 7px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #6a6a6a;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 15px;
        border: none;
        background: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    QScrollBar:horizontal {
        border: none;
        background: #3c3c3c;
        height: 14px;
        margin: 0 15px 0 15px;
        border-radius: 7px;
    }
    QScrollBar::handle:horizontal {
        background-color: #5a5a5a;
        min-width: 30px;
        border-radius: 7px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #6a6a6a;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 15px;
        border: none;
        background: none;
    }
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: none;
    }
"""


class PreviewWindow(QWidget):
    def __init__(self, image_grid, row, col):
        super().__init__()
        self.image_grid = image_grid
        self.current_row = row
        self.current_col = col

        self.setWindowTitle("Image Preview")
        self.setGeometry(150, 150, 800, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.update_image()

    def update_image(self):
        image_path = self.image_grid[self.current_row][self.current_col]
        pixmap = QPixmap(image_path)
        
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.setWindowTitle(f"Image Preview - {os.path.basename(image_path)}")

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        if key == Qt.Key_Right:
            self.current_col = (self.current_col + 1) % len(
                self.image_grid[self.current_row]
            )
        elif key == Qt.Key_Left:
            self.current_col = (
                self.current_col - 1 + len(self.image_grid[self.current_row])
            ) % len(self.image_grid[self.current_row])
        elif key == Qt.Key_Down:
            self.current_row = (self.current_row + 1) % len(self.image_grid)
            self.current_col = min(
                self.current_col, len(self.image_grid[self.current_row]) - 1
            )
        elif key == Qt.Key_Up:
            self.current_row = (
                self.current_row - 1 + len(self.image_grid)
            ) % len(self.image_grid)
            self.current_col = min(
                self.current_col, len(self.image_grid[self.current_row]) - 1
            )
        elif key == Qt.Key_Escape:
            self.close()

        self.update_image()

    def resizeEvent(self, event: QResizeEvent):
        self.update_image()


class ImageGrid(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Grid Viewer")
        self.setGeometry(100, 100, 1200, 800)
        self.setAcceptDrops(True)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # --- Welcome Screen Label ---
        self.welcome_label = QLabel()
        self.welcome_label.setText(
            """
            <div style='text-align: center;'>
                <h1 style='font-size: 24pt; color: #ffffff;'>Image Grid Viewer</h1>
                <p style='font-size: 12pt; color: #aaaaaa;'>
                    Drag and drop a folder containing your images to begin.
                </p>
                <p style='font-size: 11pt; color: #888888;'>
                    For example, the <b>samples</b> folder from 
                    <a href='https://github.com/ostris/ai-toolkit'>Ostris's AI-Toolkit</a>.
                </p>
            </div>
            """
        )
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setWordWrap(True)
        self.welcome_label.setOpenExternalLinks(True) # Make hyperlink clickable
        self.layout.addWidget(self.welcome_label)

        # --- Scroll Area for the Grid ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.scroll_area.setWidget(self.grid_widget)

        # --- Initial State ---
        self.scroll_area.hide() # Hide grid initially
        self.image_grid = []
        self.preview_window = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and os.path.isdir(files[0]):
            self.load_images(files[0])

    def load_images(self, folder_path):
        # --- Switch from Welcome Screen to Grid View ---
        self.welcome_label.hide()
        self.scroll_area.show()

        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        image_files = sorted(
            [
                f
                for f in os.listdir(folder_path)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]
        )

        images_by_steps = {}
        for filename in image_files:
            try:
                steps = int(filename.split("__")[1].split("_")[0])
                if steps not in images_by_steps:
                    images_by_steps[steps] = []
                images_by_steps[steps].append(os.path.join(folder_path, filename))
            except (IndexError, ValueError):
                pass

        self.image_grid = [
            images_by_steps[steps] for steps in sorted(images_by_steps)
        ]

        for row_idx, row_images in enumerate(self.image_grid):
            for col_idx, path in enumerate(row_images):
                thumbnail_label = QLabel()
                pixmap = QPixmap(path)
                thumbnail_label.setPixmap(
                    pixmap.scaled(
                        150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                )
                thumbnail_label.setAlignment(Qt.AlignCenter)
                
                thumbnail_label.mousePressEvent = (
                    lambda event, r=row_idx, c=col_idx: self.open_preview(r, c)
                )
                self.grid_layout.addWidget(thumbnail_label, row_idx, col_idx)

    def open_preview(self, row, col):
        self.preview_window = PreviewWindow(self.image_grid, row, col)
        self.preview_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(dark_stylesheet)
    
    main_window = ImageGrid()
    main_window.show()
    sys.exit(app.exec_())