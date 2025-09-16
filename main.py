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

# --- Dark Theme Stylesheet (unchanged) ---
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

class CustomScrollArea(QScrollArea):
    """A custom QScrollArea to handle modifier key events for scrolling and zooming."""
    def __init__(self, parent_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_window = parent_window

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        
        # Ctrl + Scroll for zooming
        if modifiers == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.parent_window.zoom_in()
            else:
                self.parent_window.zoom_out()
            event.accept()
        # Shift + Scroll for horizontal scrolling
        elif modifiers == Qt.ShiftModifier:
            h_bar = self.horizontalScrollBar()
            # Invert the delta for natural horizontal scrolling
            delta = event.angleDelta().y()
            h_bar.setValue(h_bar.value() - delta)
            event.accept()
        # Default vertical scrolling
        else:
            super().wheelEvent(event)


class PreviewWindow(QWidget):
    # This class remains unchanged
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
    # Constants for zooming
    MIN_THUMBNAIL_SIZE = 40
    MAX_THUMBNAIL_SIZE = 500
    ZOOM_STEP = 20

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Grid Viewer")
        self.setGeometry(100, 100, 1200, 800)
        self.setAcceptDrops(True)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.welcome_label = QLabel()
        self.welcome_label.setText(
            """
            <div style='text-align: center;'>
                <h1 style='font-size: 24pt; color: #ffffff;'>Image Grid Viewer</h1>
                <p style='font-size: 12pt; color: #aaaaaa;'>
                    Drag and drop a folder containing your images to begin.
                </p>
                <p style='font-size: 11pt; color: #888888;'>
                    Use <b>Ctrl + Scroll</b> to zoom and <b>Shift + Scroll</b> to scroll horizontally.
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
        self.welcome_label.setOpenExternalLinks(True)
        self.layout.addWidget(self.welcome_label)

        # Use our custom scroll area
        self.scroll_area = CustomScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.scroll_area.setWidget(self.grid_widget)

        # Initialize state
        self.scroll_area.hide()
        self.thumbnail_size = 150
        self.image_paths = [] # 2D list of image paths
        self.thumbnail_labels = [] # 2D list of QLabel widgets
        self.pixmap_cache = [] # 2D list of QPixmap objects for performance
        self.preview_window = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.load_images(path)

    def load_images(self, folder_path):
        self.welcome_label.hide()
        self.scroll_area.show()

        # Clear previous widgets and data
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.thumbnail_labels.clear()
        self.pixmap_cache.clear()
        self.image_paths.clear()

        image_files = sorted(
            [f for f in os.listdir(folder_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
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

        self.image_paths = [images_by_steps[steps] for steps in sorted(images_by_steps)]

        # Populate grid and caches
        for row_idx, row_paths in enumerate(self.image_paths):
            label_row, pixmap_row = [], []
            for col_idx, path in enumerate(row_paths):
                # Cache the pixmap for fast zooming
                pixmap = QPixmap(path)
                pixmap_row.append(pixmap)
                
                label = QLabel()
                label.setAlignment(Qt.AlignCenter)
                label.setPixmap(pixmap.scaled(self.thumbnail_size, self.thumbnail_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                label.mousePressEvent = lambda event, r=row_idx, c=col_idx: self.open_preview(r, c)
                
                self.grid_layout.addWidget(label, row_idx, col_idx)
                label_row.append(label)
            self.thumbnail_labels.append(label_row)
            self.pixmap_cache.append(pixmap_row)

    def update_thumbnail_sizes(self):
        """Iterate through all labels and update their pixmap size."""
        for row_idx, row_labels in enumerate(self.thumbnail_labels):
            for col_idx, label in enumerate(row_labels):
                # Use the cached pixmap to create a new scaled version
                pixmap = self.pixmap_cache[row_idx][col_idx]
                label.setPixmap(pixmap.scaled(self.thumbnail_size, self.thumbnail_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def zoom_in(self):
        if self.thumbnail_labels:
            self.thumbnail_size = min(self.MAX_THUMBNAIL_SIZE, self.thumbnail_size + self.ZOOM_STEP)
            self.update_thumbnail_sizes()

    def zoom_out(self):
        if self.thumbnail_labels:
            self.thumbnail_size = max(self.MIN_THUMBNAIL_SIZE, self.thumbnail_size - self.ZOOM_STEP)
            self.update_thumbnail_sizes()

    def open_preview(self, row, col):
        self.preview_window = PreviewWindow(self.image_paths, row, col)
        self.preview_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(dark_stylesheet)
    
    main_window = ImageGrid()
    main_window.show()
    sys.exit(app.exec_())