from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from copy import deepcopy
from gameobject import GameObject
from scene_view import SceneView
from camera import Camera

class AddGameObjectDialog(QDialog):
    def __init__(self, scene_view, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New GameObject")
        self.layout = QGridLayout(self)
        self.scene_view = scene_view

        self.items = [
            {"name": "GameObject", "icon": "icons/GameObject.png", "properties": self.default_properties()},
            {"name": "Camera", "icon": "icons/Camera.png", "properties": self.camera_properties()},
        ]

        self.populate_grid()
        self.button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box, len(self.items) // 3 + 1, 0, 1, 3)

    def default_properties(self):
        return {
            "position": (100, 100),
            "size": (50, 50),
            "color": (255, 255, 255, 255),
            "rotation": 0.0,
            "scale": 1.0,
            "image_path": None,
            "layer": 0,
            "overlay_color": (0, 0, 0, 0)
        }

    def camera_properties(self):
        return {
            "position": (500, 150),
            "size": (100, 100),
            "rotation": 60,
            "fov": 60
        }

    def populate_grid(self):
        row, col = 0, 0
        for item in self.items:
            button = QToolButton()
            button.setIcon(QIcon(item["icon"]))
            button.setIconSize(QSize(64, 64))
            button.setText(item["name"])
            button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            button.clicked.connect(lambda _, it=item: self.add_game_object(it))
            self.layout.addWidget(button, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def add_game_object(self, item):
        self.selected_item = deepcopy(item)
        self.scene_view.repaint()
        self.accept()

    def get_selected_item(self):
        return self.selected_item


class Hierarchy(QWidget):
    def __init__(self, scene_view):
        super().__init__()

        self.scene_view = scene_view

        # Configuração do layout principal
        self.layout = QVBoxLayout()

        # Criação da árvore hierárquica
        self.hierarchy_tree = QTreeWidget()
        self.hierarchy_tree.setHeaderHidden(True)  # Esconde o cabeçalho
        self.hierarchy_tree.setStyleSheet("background-color: #333; color: #FFF; border: 1px solid #777;")  # Estilo visual
        self.hierarchy_tree.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Barras de rolagem
        self.hierarchy_tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.hierarchy_tree.setDragDropMode(QAbstractItemView.InternalMove)  # Habilita movimentação de itens
        self.hierarchy_tree.setDefaultDropAction(Qt.MoveAction)  # Ação padrão ao soltar
        self.hierarchy_tree.setEditTriggers(QAbstractItemView.DoubleClicked)  # Edição ao dar duplo clique
        self.hierarchy_tree.setSelectionMode(QAbstractItemView.ExtendedSelection)  # Seleção estendida
        
        # Botão para adicionar novos objetos de jogo
        self.add_button = QPushButton("Add GameObject")
        self.add_button.clicked.connect(self.show_add_game_object_dialog)  # Conecta o clique do botão a um método
        self.root_item = None  # Definimos o root_item como None inicialmente

        # Adiciona a árvore e o botão ao layout
        self.layout.addWidget(self.hierarchy_tree)
        self.layout.addWidget(self.add_button)
        self.setLayout(self.layout)

        # Conecta sinais de inserção e movimentação de linhas na árvore
        self.hierarchy_tree.model().rowsInserted.connect(self.on_rows_inserted)
        self.hierarchy_tree.model().rowsMoved.connect(self.on_rows_moved)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()
    

    
    def set_root_item(self, root_object):
        if self.root_item is None:
            # Utiliza o root_object para definir o root_item e o adiciona na hierarquia
            self.root_item = QTreeWidgetItem([root_object.name])
            self.hierarchy_tree.addTopLevelItem(self.root_item)
            self.root_item.setExpanded(True)

    def add_gameobject(self, game_object):
        item = QTreeWidgetItem([game_object.name])
        if self.root_item:
            self.root_item.addChild(item)
        else:
            self.hierarchy_tree.addTopLevelItem(item)



    def show_add_game_object_dialog(self):
        dialog = AddGameObjectDialog(self.scene_view, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_item = dialog.get_selected_item()
            properties = selected_item["properties"]
            unique_name = self.generate_unique_name(selected_item["name"])

            parent_item = self.hierarchy_tree.currentItem()
            parent_object = self.parent().parent().object_dict.get(parent_item.text(0)) if parent_item else None

            if selected_item["name"] == "Camera":
                new_game_object = Camera(
                    unique_name,
                    position=properties["position"],
                    size=properties["size"],
                    fov=properties["fov"],
                    scene_view=self.scene_view
                )
            else:
                new_game_object = GameObject(
                    unique_name,
                    position=properties["position"],
                    size=properties["size"],
                    color=properties["color"],
                    rotation=properties["rotation"],
                    scale=properties["scale"],
                    scene_view=self.scene_view,
                    image_path=properties["image_path"]
                )
                new_game_object.set_overlay_color(QColor(*properties["overlay_color"]))
                new_game_object.set_layer(properties["layer"])

            self.scene_view.add_game_object(new_game_object)

            if parent_object:
                parent_object.add_child(new_game_object)
                new_game_object.set_parent(parent_object)

            self.parent().parent().add_to_hierarchy_and_dict(new_game_object)

    def generate_unique_name(self, base_name):
        existing_names = self.get_all_item_names()
        if base_name not in existing_names:
            return base_name

        i = 1
        new_name = f"{base_name} ({i})"
        while new_name in existing_names:
            i += 1
            new_name = f"{base_name} ({i})"
        return new_name

    def get_all_item_names(self):
        def get_item_names(item):
            names = [item.text(0)]
            for i in range(item.childCount()):
                names.extend(get_item_names(item.child(i)))
            return names

        names = []
        for i in range(self.hierarchy_tree.topLevelItemCount()):
            names.extend(get_item_names(self.hierarchy_tree.topLevelItem(i)))
        return names

    def update_cam(self, item):
        selected_item_text = item.text(0)
        selected_object = self.parent().parent().object_dict.get(selected_item_text)
        if selected_object:
            self.parent().parent().properties.set_selected_object(selected_object)
            if isinstance(selected_object, Camera):
                self.scene_view.set_active_camera(selected_object)

    def on_rows_inserted(self, parent_index, start, end):
        parent_item = self.hierarchy_tree.itemFromIndex(parent_index)
        for row in range(start, end + 1):
            child_item = self.hierarchy_tree.itemFromIndex(parent_index.child(row, 0))
            if child_item and parent_item:
                child_object = self.parent().parent().object_dict.get(child_item.text(0))
                parent_object = self.parent().parent().object_dict.get(parent_item.text(0))
                if child_object and parent_object:
                    if child_object.parent:
                        child_object.parent.children.remove(child_object)
                        child_object.set_parent(None)
                    parent_object.add_child(child_object)
                    child_object.set_parent(parent_object)

    def on_rows_moved(self, source_parent, source_start, source_end, destination_parent, destination_row):
        # Verifica se o destino não é o root_item ou se o destino não é válido.
        if not destination_parent.isValid() or destination_parent != self.hierarchy_tree.indexFromItem(self.root_item):
            return  # Cancela a ação se o destino não for o root_item ou não for válido
        
        source_parent_item = self.hierarchy_tree.itemFromIndex(source_parent)
        destination_parent_item = self.hierarchy_tree.itemFromIndex(destination_parent)

        for row in range(source_start, source_end + 1):
            moved_item = self.hierarchy_tree.itemFromIndex(source_parent.child(row, 0))
            if moved_item:
                moved_object = self.parent().parent().object_dict.get(moved_item.text(0))

                # Impede mover para fora do root_item
                if destination_parent_item != self.root_item:  # Verificação direta
                    return  # Cancela a ação se o item está sendo movido para fora do root_item

                # Remove o objeto do seu pai anterior, se houver
                if moved_object and moved_object.parent:
                    moved_object.parent.remove_child(moved_object)
                    moved_object.set_parent(None)

                # Adiciona o objeto ao novo pai se for válido
                if destination_parent_item == self.root_item:
                    if moved_object:
                        moved_object.set_parent(None)
                else:
                    destination_object = self.parent().parent().object_dict.get(destination_parent_item.text(0))
                    if moved_object and destination_object:
                        destination_object.add_child(moved_object)
                        moved_object.set_parent(destination_object)

        self.hierarchy_tree.expandAll()




    def dropEvent(self, event):
        super(Hierarchy, self).dropEvent(event)
        
        # Impede a movimentação para fora do nó raiz
        current_item = self.hierarchy_tree.currentItem()
        if current_item and current_item.parent() is None:
            self.root_item.addChild(current_item)
        
        self.on_rows_moved(
            self.hierarchy_tree.currentIndex().parent(),
            self.hierarchy_tree.currentIndex().row(),
            self.hierarchy_tree.currentIndex().row(),
            self.hierarchy_tree.currentIndex().parent(),
            self.hierarchy_tree.currentIndex().row()
        )
