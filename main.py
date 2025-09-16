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
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
)
from PyQt5.QtGui import QPixmap, QKeyEvent, QResizeEvent, QPainter
from PyQt5.QtCore import Qt, QPoint

# --- Dark Theme Stylesheet (unchanged) ---
dark_stylesheet = """
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        font-family: Segoe UI;
        font-size: 10pt;
    }
    QMainWindow, QGraphicsView {
        background-color: #2b2b2b;
        border: none;
    }
    QLabel#FooterLabel {
        color: #aaaaaa;
        font-size: 9pt;
        padding: 4px 8px;
        background-color: #222222;
        border-top: 1px solid #3c3c3c;
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
    QScrollBar:vertical {
        border: none; background: #3c3c3c; width: 14px; margin: 15px 0 15px 0; border-radius: 7px;
    }
    QScrollBar::handle:vertical { background-color: #5a5a5a; min-height: 30px; border-radius: 7px; }
    QScrollBar::handle:vertical:hover { background-color: #6a6a6a; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 15px; border: none; background: none; }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
    QScrollBar:horizontal {
        border: none; background: #3c3c3c; height: 14px; margin: 0 15px 0 15px; border-radius: 7px;
    }
    QScrollBar::handle:horizontal { background-color: #5a5a5a; min-width: 30px; border-radius: 7px; }
    QScrollBar::handle:horizontal:hover { background-color: #6a6a6a; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 15px; border: none; background: none; }
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
"""

class CustomScrollArea(QScrollArea):
    # This class remains unchanged
    def __init__(self, parent_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_window = parent_window

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0: self.parent_window.zoom_in()
            else: self.parent_window.zoom_out()
            event.accept()
        elif modifiers == Qt.ShiftModifier:
            h_bar = self.horizontalScrollBar()
            delta = event.angleDelta().y()
            h_bar.setValue(h_bar.value() - delta)
            event.accept()
        else:
            super().wheelEvent(event)

class InteractiveGraphicsView(QGraphicsView):
    """The view that handles zooming and panning."""
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.is_panning = False
        self.last_mouse_pos = QPoint()

    def wheelEvent(self, event):
        zoom_factor = 1.15
        if event.angleDelta().y() > 0: self.scale(zoom_factor, zoom_factor)
        else: self.scale(1 / zoom_factor, 1 / zoom_factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.is_panning = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_panning:
            delta = event.pos() - self.last_mouse_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.last_mouse_pos = event.pos()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.is_panning = False
            self.setCursor(Qt.ArrowCursor)
        else:
            super().mouseReleaseEvent(event)
            
    def keyPressEvent(self, event: QKeyEvent):
        """Intercept arrow keys and Escape to prevent default QGraphicsView panning/closing."""
        key = event.key()
        if key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right, Qt.Key_Escape):
            event.ignore() # Let the parent (PreviewWindow) handle these keys
        else:
            super().keyPressEvent(event)


class PreviewWindow(QWidget):
    """A QWidget container for the interactive view and the footer."""
    def __init__(self, image_paths, row, col):
        super().__init__()
        self.image_paths = image_paths
        self.current_row = row
        self.current_col = col

        # --- Scene and View setup ---
        self.scene = QGraphicsScene(self)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self.view = InteractiveGraphicsView(self.scene) # Use our custom view

        # --- Footer Label ---
        self.footer_label = QLabel()
        self.footer_label.setObjectName("FooterLabel") # For styling
        
        # --- Layout ---
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.view)
        layout.addWidget(self.footer_label)
        self.setLayout(layout)

        # --- Window setup ---
        self.setWindowTitle("Image Preview")
        self.setGeometry(150, 150, 800, 600)
        self.update_image()

    def update_image(self):
        """Loads a new image, updates the footer, and fits the image to the view."""
        path = self.image_paths[self.current_row][self.current_col]
        filename = os.path.basename(path)
        
        # Load pixmap
        pixmap = QPixmap(path)
        self.pixmap_item.setPixmap(pixmap)
        
        # Reset view to fit the whole image in view
        self.view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
        self.setWindowTitle(f"Image Preview - {filename}")

        # Update footer
        try:
            steps = int(filename.split("__")[1].split("_")[0])
            left_text = f"Steps: {steps}"
        except (IndexError, ValueError):
            left_text = "Steps: N/A"
        
        right_text = "Scroll to zoom; MMB to pan"
        footer_html = f"""
            <table width='100%'><tr>
            <td align='left'>{left_text}</td>
            <td align='right'>{right_text}</td>
            </tr></table>
        """
        self.footer_label.setText(footer_html)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle arrow key navigation between images and Escape to close."""
        key = event.key()
        if key == Qt.Key_Right:
            self.current_col = (self.current_col + 1) % len(self.image_paths[self.current_row])
        elif key == Qt.Key_Left:
            self.current_col = (self.current_col - 1 + len(self.image_paths[self.current_row])) % len(self.image_paths[self.current_row])
        elif key == Qt.Key_Down:
            self.current_row = (self.current_row + 1) % len(self.image_paths)
            self.current_col = min(self.current_col, len(self.image_paths[self.current_row]) - 1)
        elif key == Qt.Key_Up:
            self.current_row = (self.current_row - 1 + len(self.image_paths)) % len(self.image_paths)
            self.current_col = min(self.current_col, len(self.image_paths[self.current_row]) - 1)
        elif key == Qt.Key_Escape:
            self.close()
        
        # When a key is pressed to change image, update it
        self.update_image()

    def resizeEvent(self, event: QResizeEvent):
        """Fit the image to the view when the window is resized."""
        self.view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
        super().resizeEvent(event)


class ImageGrid(QMainWindow):
    # This class is unchanged from the previous version
    MIN_THUMBNAIL_SIZE, MAX_THUMBNAIL_SIZE, ZOOM_STEP = 40, 500, 20

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Grid Viewer"); self.setGeometry(100, 100, 1200, 800); self.setAcceptDrops(True)
        self.central_widget = QWidget(); self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.welcome_label = QLabel()
        self.welcome_label.setText(
            """<div style='text-align: center;'><h1 style='font-size: 24pt;'>Image Grid Viewer</h1>
               <p style='font-size: 12pt; color: #aaaaaa;'>Drag and drop a folder to begin.</p>
               <p style='font-size: 11pt; color: #888888;'>Use <b>Ctrl+Scroll</b> to zoom thumbnails and <b>Shift+Scroll</b> to scroll horizontally.</p>
               <p style='font-size: 11pt; color: #888888;'>Example folder: <b>samples</b> from <a href='https://github.com/ostris/ai-toolkit'>Ostris's AI-Toolkit</a>.</p></div>""")
        self.welcome_label.setAlignment(Qt.AlignCenter); self.welcome_label.setWordWrap(True); self.welcome_label.setOpenExternalLinks(True)
        self.layout.addWidget(self.welcome_label)
        self.scroll_area = CustomScrollArea(self); self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)
        self.grid_widget = QWidget(); self.grid_layout = QGridLayout(self.grid_widget)
        self.scroll_area.setWidget(self.grid_widget)
        self.scroll_area.hide()
        self.thumbnail_size = 150
        self.image_paths = []; self.thumbnail_labels = []; self.pixmap_cache = []
        self.preview_window = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            path = urls[0].toLocalFile()
            if os.path.isdir(path): self.load_images(path)

    def load_images(self, folder_path):
        self.welcome_label.hide(); self.scroll_area.show()
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget: widget.setParent(None)
        self.thumbnail_labels.clear(); self.pixmap_cache.clear(); self.image_paths.clear()
        image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
        images_by_steps = {}
        for filename in image_files:
            try:
                steps = int(filename.split("__")[1].split("_")[0])
                if steps not in images_by_steps: images_by_steps[steps] = []
                images_by_steps[steps].append(os.path.join(folder_path, filename))
            except (IndexError, ValueError): pass
        self.image_paths = [images_by_steps[steps] for steps in sorted(images_by_steps)]
        for r, row_paths in enumerate(self.image_paths):
            label_row, pixmap_row = [], []
            for c, path in enumerate(row_paths):
                pixmap = QPixmap(path); pixmap_row.append(pixmap)
                label = QLabel(); label.setAlignment(Qt.AlignCenter)
                label.setPixmap(pixmap.scaled(self.thumbnail_size, self.thumbnail_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                label.mousePressEvent = lambda e, r=r, c=c: self.open_preview(r, c)
                self.grid_layout.addWidget(label, r, c); label_row.append(label)
            self.thumbnail_labels.append(label_row); self.pixmap_cache.append(pixmap_row)

    def update_thumbnail_sizes(self):
        for r, row in enumerate(self.thumbnail_labels):
            for c, label in enumerate(row):
                pixmap = self.pixmap_cache[r][c]
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