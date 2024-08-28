from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QGroupBox, QLabel, QListWidget, QAbstractItemView
)
from PyQt5.QtCore import Qt

class ParentsPanel(QWidget):
    def __init__(self, scene_view):
        super().__init__()
        self.scene_view = scene_view
        self.selected_object = None

        self.init_ui()

    def init_ui(self):
        """Configura a interface do usuário para o painel de parentesco."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        parents_group = QGroupBox("Parents")
        parents_layout = QGridLayout()

        self.parent_list = QListWidget()
        self.child_list = QListWidget()

        self.parent_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.child_list.setSelectionMode(QAbstractItemView.SingleSelection)

        self.parent_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.child_list.setDragDropMode(QAbstractItemView.InternalMove)

        parents_layout.addWidget(QLabel("Objeto Pai:"), 0, 0)
        parents_layout.addWidget(self.parent_list, 1, 0)

        parents_layout.addWidget(QLabel("Objeto Filho:"), 0, 1)
        parents_layout.addWidget(self.child_list, 1, 1)

        parents_group.setLayout(parents_layout)
        layout.addWidget(parents_group)

        self.connect_signals()

    def connect_signals(self):
        """Conecta os sinais de mudanças nos parentescos."""
        self.parent_list.model().rowsMoved.connect(self.update_parent)
        self.child_list.model().rowsMoved.connect(self.update_child)

    def set_selected_object(self, selected_object):
        """Define o objeto selecionado e atualiza as listas de pai e filho."""
        self.selected_object = selected_object
        self.update_lists()

    def update_lists(self):
        """Atualiza as listas de pai e filho com os objetos da cena."""
        self.parent_list.clear()
        self.child_list.clear()

        if not self.selected_object:
            return

        # Preenchendo a lista de objetos pais e filhos
        for obj in self.scene_view.objects:
            self.parent_list.addItem(obj.name)
            self.child_list.addItem(obj.name)

        # Destacando o pai e os filhos do objeto selecionado
        if self.selected_object.parent:
            parent_item = self.parent_list.findItems(self.selected_object.parent.name, Qt.MatchExactly)[0]
            parent_item.setSelected(True)

        for child in self.selected_object.children:
            child_item = self.child_list.findItems(child.name, Qt.MatchExactly)[0]
            child_item.setSelected(True)

    def update_parent(self):
        """Atualiza o objeto pai do objeto selecionado."""
        if not self.selected_object:
            return

        selected_parent_items = self.parent_list.selectedItems()
        if selected_parent_items:
            parent_name = selected_parent_items[0].text()
            new_parent = next(obj for obj in self.scene_view.objects if obj.name == parent_name)
            self.selected_object.set_parent(new_parent)
        else:
            self.selected_object.set_parent(None)

        self.notify_change()

    def update_child(self):
        """Atualiza os objetos filhos do objeto selecionado."""
        if not self.selected_object:
            return

        selected_child_items = self.child_list.selectedItems()
        new_children = [obj for obj in self.scene_view.objects if obj.name in [item.text() for item in selected_child_items]]

        self.selected_object.set_children(new_children)
        self.notify_change()

    def notify_change(self):
        """Notifica mudanças e atualiza a cena."""
        self.scene_view.repaint()
        self.update_lists()
