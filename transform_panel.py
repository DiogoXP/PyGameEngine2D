from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QGridLayout, QGroupBox, QLabel
)
from PyQt5.QtCore import Qt

class TransformPanel(QWidget):
    def __init__(self, scene_view):
        super().__init__()
        self.selected_object = None
        self.scene_view = scene_view

        self.init_ui()

    def init_ui(self):
        """Configura a interface do usuário para o painel de transformações."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        transform_group = QGroupBox("Transformações")
        transform_layout = QGridLayout()

        self.position_x_input = self.create_line_edit()
        self.position_y_input = self.create_line_edit()
        self.size_width_input = self.create_line_edit()
        self.size_height_input = self.create_line_edit()
        self.color_input = self.create_line_edit()
        self.rotation_input = self.create_line_edit()
        self.scale_input = self.create_line_edit()
        self.is_child_label = QLabel()

        self.add_labeled_input(transform_layout, "Posição X:", self.position_x_input, 0, 0)
        self.add_labeled_input(transform_layout, "Posição Y:", self.position_y_input, 0, 2)
        self.add_labeled_input(transform_layout, "Largura:", self.size_width_input, 1, 0)
        self.add_labeled_input(transform_layout, "Altura:", self.size_height_input, 1, 2)
        self.add_labeled_input(transform_layout, "Cor (RGBA):", self.color_input, 2, 0, 1, 4)
        self.add_labeled_input(transform_layout, "Rotação:", self.rotation_input, 3, 0)
        self.add_labeled_input(transform_layout, "Escala:", self.scale_input, 3, 2)
        self.add_labeled_input(transform_layout, "É Filho:", self.is_child_label, 4, 0, 1, 4)

        transform_group.setLayout(transform_layout)
        layout.addWidget(transform_group)

        self.connect_signals()

    def create_line_edit(self):
        """Cria e retorna um QLineEdit."""
        return QLineEdit()

    def add_labeled_input(self, layout, label_text, input_widget, row, col, row_span=1, col_span=1):
        """Adiciona um rótulo e um campo de entrada ao layout."""
        layout.addWidget(QLabel(label_text), row, col)
        layout.addWidget(input_widget, row, col + 1, row_span, col_span)

    def connect_signals(self):
        """Conecta os sinais de texto alterado aos métodos de atualização correspondentes."""
        self.position_x_input.textChanged.connect(lambda text: self.update_position(text, axis='x'))
        self.position_y_input.textChanged.connect(lambda text: self.update_position(text, axis='y'))
        self.size_width_input.textChanged.connect(lambda text: self.update_size(text, dimension='width'))
        self.size_height_input.textChanged.connect(lambda text: self.update_size(text, dimension='height'))
        self.color_input.textChanged.connect(self.update_color)
        self.rotation_input.textChanged.connect(self.update_rotation)
        self.scale_input.textChanged.connect(self.update_scale)

    def set_selected_object(self, selected_object):
        """Define o objeto selecionado e atualiza os campos do painel."""
        self.selected_object = selected_object
        self.update_fields()

    def update_fields(self):
        """Atualiza os campos do painel com as propriedades do objeto selecionado."""
        if not self.selected_object:
            return

        self.position_x_input.setText(str(self.selected_object.position[0]))
        self.position_y_input.setText(str(self.selected_object.position[1]))
        self.size_width_input.setText(str(self.selected_object.size[0]))
        self.size_height_input.setText(str(self.selected_object.size[1]))

        if hasattr(self.selected_object, 'color'):
            self.color_input.setText(','.join(map(str, self.selected_object.color)))
        
        if hasattr(self.selected_object, 'rotation'):
            self.rotation_input.setText(str(self.selected_object.rotation))
        
        if hasattr(self.selected_object, 'scale'):
            self.scale_input.setText(str(self.selected_object.scale))
        
        self.is_child_label.setText("Sim" if self.selected_object.parent else "Não")

    def update_position(self, text, axis):
        """Atualiza a posição do objeto selecionado com base no texto de entrada."""
        if not self.selected_object:
            return

        try:
            value = float(text)
            position = list(self.selected_object.position)
            if axis == 'x':
                position[0] = value
            elif axis == 'y':
                position[1] = value
            self.selected_object.set_position(tuple(position))
            self.notify_change()
        except ValueError:
            pass

    def update_size(self, text, dimension):
        """Atualiza o tamanho do objeto selecionado com base no texto de entrada."""
        if not self.selected_object:
            return

        try:
            value = float(text)
            size = list(self.selected_object.size)
            if dimension == 'width':
                size[0] = value
            elif dimension == 'height':
                size[1] = value
            self.selected_object.size = tuple(size)
            if hasattr(self.selected_object, 'update_image'):
                self.selected_object.update_image()
            self.notify_change()
        except ValueError:
            pass

    def update_color(self, text):
        """Atualiza a cor do objeto selecionado com base no texto de entrada."""
        if not self.selected_object or not hasattr(self.selected_object, 'color'):
            return

        try:
            color_values = list(map(int, text.split(',')))
            if len(color_values) == 4:
                self.selected_object.color = tuple(color_values)
                if hasattr(self.selected_object, 'update_image'):
                    self.selected_object.update_image()
                self.notify_change()
        except ValueError:
            pass

    def update_rotation(self, text):
        """Atualiza a rotação do objeto selecionado com base no texto de entrada."""
        if not self.selected_object or not hasattr(self.selected_object, 'rotation'):
            return

        try:
            self.selected_object.rotation = float(text)
            if hasattr(self.selected_object, 'update_image'):
                self.selected_object.update_image()
            self.notify_change()
        except ValueError:
            pass

    def update_scale(self, text):
        """Atualiza a escala do objeto selecionado com base no texto de entrada."""
        if not self.selected_object or not hasattr(self.selected_object, 'scale'):
            return

        try:
            self.selected_object.scale = float(text)
            if hasattr(self.selected_object, 'update_image'):
                self.selected_object.update_image()
            self.notify_change()
        except ValueError:
            pass

    def notify_change(self):
        """Notifica mudanças e atualiza a cena."""
        self.scene_view.repaint()
        self.selected_object.store_original_state()
        self.update_fields()
