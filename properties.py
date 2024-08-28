from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton, QDialog, QListWidget, QListWidgetItem, QDialogButtonBox
)
from PyQt5.QtGui import QIcon
from transform_panel import TransformPanel
from script_panel import ScriptPanel
from image_panel import ImagePanel

class Properties(QWidget):
    def __init__(self, scene_view):
        super().__init__()
        self.scene_view = scene_view
        self.selected_object = None
        self.panels = {}  # Dicionário para armazenar painéis por objeto

        self.setup_ui()

    def setup_ui(self):
        """Configura a interface do usuário."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.properties_label = QLabel("Properties")
        self.properties_label.setStyleSheet("color: #FFF;")
        main_layout.addWidget(self.properties_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        self.add_component_button = QPushButton("Add Component")
        self.add_component_button.setStyleSheet("color: #FFF;")
        self.add_component_button.clicked.connect(self.show_add_component_dialog)
        main_layout.addWidget(self.add_component_button)

    def set_selected_object(self, selected_object):
        """Define o objeto selecionado e atualiza os painéis."""
        self.selected_object = selected_object
        self.update_panels()

    def update_panels(self):
        """Atualiza a lista de painéis com base no objeto selecionado."""
        self.clear_panels()

        if self.selected_object:
            self.ensure_panels_for_selected_object()
            for panel in self.panels[self.selected_object]:
                self.scroll_layout.addWidget(panel)
            self.scroll_layout.addStretch()

    def clear_panels(self):
        """Remove todos os painéis atuais da interface."""
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def ensure_panels_for_selected_object(self):
        """Garante que os painéis necessários para o objeto selecionado estejam disponíveis."""
        if self.selected_object not in self.panels:
            self.panels[self.selected_object] = []

        # Remove o ImagePanel se o objeto não suportar update_image
        if not hasattr(self.selected_object, 'update_image'):
            self.panels[self.selected_object] = [
                panel for panel in self.panels[self.selected_object]
                if not isinstance(panel, ImagePanel)
            ]

    def show_add_component_dialog(self):
        """Exibe o diálogo para adicionar um novo componente."""
        dialog = AddComponentDialog(self.selected_object, self)
        dialog.setModal(True)
        dialog.exec_()
        if dialog.result() == QDialog.Accepted:
            selected_component = dialog.get_selected_component()
            if selected_component:
                self.add_component(selected_component)

    def add_component(self, component_name):
        """Adiciona um novo componente ao objeto selecionado."""
        if self.selected_object is None:
            return  # Se nenhum objeto estiver selecionado, não faça nada

        panel = None

        if component_name == "Transform":
            if any(isinstance(panel, TransformPanel) for panel in self.panels.get(self.selected_object, [])):
                print("Transform component already added.")
                return
            panel = TransformPanel(self.scene_view)

        elif component_name == "Script":
            if any(isinstance(panel, ScriptPanel) for panel in self.panels.get(self.selected_object, [])):
                print("Script component already added.")
                return
            panel = ScriptPanel(self.scene_view)

        elif component_name == "Image":
            if not hasattr(self.selected_object, 'update_image'):
                print("Selected object does not support Image component.")
                return
            if any(isinstance(panel, ImagePanel) for panel in self.panels.get(self.selected_object, [])):
                print("Image component already added.")
                return
            panel = ImagePanel(self.scene_view)

        if panel:
            panel.set_selected_object(self.selected_object)
            self.panels[self.selected_object].append(panel)
            self.update_panels()


class AddComponentDialog(QDialog):
    def __init__(self, selected_object, parent=None):
        super().__init__(parent)
        self.selected_object = selected_object
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface do diálogo para adicionar componentes."""
        self.setWindowTitle("Add Component")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()
        self.component_list = QListWidget()
        self.populate_component_list()
        layout.addWidget(self.component_list)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def populate_component_list(self):
        """Preenche a lista de componentes com base no objeto selecionado."""
        components = [("Transform", "icons/Transform.png"),
                      ("Script", "icons/Script.png")]
        if hasattr(self.selected_object, 'update_image'):
            components.append(("Image", "icons/Image.png"))

        for component_name, icon_path in components:
            item = QListWidgetItem(QIcon(icon_path), component_name)
            self.component_list.addItem(item)

    def get_selected_component(self):
        """Retorna o nome do componente selecionado no diálogo."""
        selected_items = self.component_list.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None
