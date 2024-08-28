from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QColorDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor

class ImagePanel(QWidget):
    def __init__(self, scene_view):
        super().__init__()
        self.selected_object = None
        self.scene_view = scene_view

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Textura
        title_label = QLabel("Textura")
        title_label.setAlignment(Qt.AlignCenter)

        self.image_display = QLabel()
        self.image_display.setFixedSize(50, 50)
        self.image_display.setStyleSheet("border: 1px solid black; border-radius: 5px;")
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.mousePressEvent = self.load_image

        image_layout = QHBoxLayout()
        image_layout.addWidget(title_label)
        image_layout.addWidget(self.image_display)

        layout.addLayout(image_layout)

        # Campos de Offset e Tiling
        self.offset_x_edit = self.create_labeled_field("Offset X", layout)
        self.offset_x_edit.textChanged.connect(self.update_offset_x)

        self.offset_y_edit = self.create_labeled_field("Offset Y", layout)
        self.offset_y_edit.textChanged.connect(self.update_offset_y)

        self.tiling_x_edit = self.create_labeled_field("Tiling X", layout)
        self.tiling_x_edit.textChanged.connect(self.update_tiling_x)

        self.tiling_y_edit = self.create_labeled_field("Tiling Y", layout)
        self.tiling_y_edit.textChanged.connect(self.update_tiling_y)

        # Botão de Cor de Sobreposição
        overlay_color_layout = QHBoxLayout()
        overlay_color_label = QLabel("Cor de Sobreposição")
        overlay_color_label.setAlignment(Qt.AlignCenter)
        
        self.overlay_color_button = QPushButton()
        self.overlay_color_button.setFixedSize(50, 50)
        self.overlay_color_button.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: #000000;")
        self.overlay_color_button.clicked.connect(self.choose_color)
        
        overlay_color_layout.addWidget(overlay_color_label)
        overlay_color_layout.addWidget(self.overlay_color_button)
        layout.addLayout(overlay_color_layout)

        # Campo de Alpha de Sobreposição
        self.overlay_alpha_edit = self.create_labeled_field("Alpha de Sobreposição", layout)
        self.overlay_alpha_edit.textChanged.connect(self.update_overlay_alpha)

        # Campo de Camada
        self.layer_edit = self.create_labeled_field("Camada", layout)
        self.layer_edit.textChanged.connect(self.update_layer)

    def create_labeled_field(self, label_text, layout):
        container = QWidget()
        container_layout = QHBoxLayout()
        container.setLayout(container_layout)

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)

        line_edit = QLineEdit()
        line_edit.setStyleSheet("border: 1px solid black; border-radius: 5px; padding: 2px;")
        
        container_layout.addWidget(label)
        container_layout.addWidget(line_edit)

        layout.addWidget(container)

        return line_edit

    def set_selected_object(self, selected_object):
        self.selected_object = selected_object
        if self.selected_object:
            self.update_fields()

    def update_fields(self):
        if self.selected_object:
            if hasattr(self.selected_object, 'image_path') and self.selected_object.image_path:
                pixmap = QPixmap(self.selected_object.image_path)
                self.image_display.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio))
            else:
                self.image_display.clear()
                
            self.offset_x_edit.setText(str(getattr(self.selected_object, 'offset_x', '')))
            self.offset_y_edit.setText(str(getattr(self.selected_object, 'offset_y', '')))
            self.tiling_x_edit.setText(str(getattr(self.selected_object, 'tiling_x', '')))
            self.tiling_y_edit.setText(str(getattr(self.selected_object, 'tiling_y', '')))
            self.overlay_alpha_edit.setText(str(getattr(self.selected_object, 'overlay_color', QColor(0, 0, 0, 255)).alpha()))
            self.layer_edit.setText(str(getattr(self.selected_object, 'layer', '')))

            if hasattr(self.selected_object, 'overlay_color'):
                color = self.selected_object.overlay_color
                self.overlay_color_button.setStyleSheet(f"background-color: {color.name()};")

    def load_image(self, event):
        if self.selected_object:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "Selecione uma imagem", "", "Imagens (*.png *.jpg *.bmp)")
            if file_path:
                self.selected_object.set_image(file_path)
                self.update_fields()

    def choose_color(self):
        if self.selected_object:
            # Temporarily remove the always-on-top hint
            self.window().setWindowFlags(self.window().windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.window().show()

            # Open the color dialog
            color = QColorDialog.getColor()
            if color.isValid():
                self.selected_object.overlay_color = color
                self.overlay_color_button.setStyleSheet(f"background-color: {color.name()};")
                if hasattr(self.selected_object, 'update_image'):
                    self.selected_object.update_image()
                self.notify_change()

            # Restore the always-on-top hint
            self.window().setWindowFlags(self.window().windowFlags() | Qt.WindowStaysOnTopHint)
            self.window().show()

    def update_offset_x(self, value):
        if self.selected_object:
            try:
                self.selected_object.offset_x = float(value)
                if hasattr(self.selected_object, 'update_image'):
                    self.selected_object.update_image()
                self.notify_change()
            except ValueError:
                pass

    def update_offset_y(self, value):
        if self.selected_object:
            try:
                self.selected_object.offset_y = float(value)
                if hasattr(self.selected_object, 'update_image'):
                    self.selected_object.update_image()
                self.notify_change()
            except ValueError:
                pass

    def update_tiling_x(self, value):
        if self.selected_object:
            try:
                self.selected_object.tiling_x = float(value)
                if hasattr(self.selected_object, 'update_image'):
                    self.selected_object.update_image()
                self.notify_change()
            except ValueError:
                pass

    def update_tiling_y(self, value):
        if self.selected_object:
            try:
                self.selected_object.tiling_y = float(value)
                if hasattr(self.selected_object, 'update_image'):
                    self.selected_object.update_image()
                self.notify_change()
            except ValueError:
                pass

    def update_overlay_alpha(self, value):
        if self.selected_object and hasattr(self.selected_object, 'overlay_color'):
            try:
                alpha = int(value)
                if 0 <= alpha <= 255:
                    color = self.selected_object.overlay_color
                    color.setAlpha(alpha)
                    self.selected_object.overlay_color = color
                    if hasattr(self.selected_object, 'update_image'):
                        self.selected_object.update_image()
                    self.notify_change()
            except ValueError:
                pass

    def update_layer(self, value):
        if self.selected_object:
            try:
                layer = int(value)
                self.selected_object.layer = layer
                self.notify_change()
                self.scene_view.update()
            except ValueError:
                pass

    def notify_change(self):
        self.scene_view.repaint()
        if not self.scene_view.running:
            if hasattr(self.selected_object, 'store_original_state'):
                self.selected_object.store_original_state()
