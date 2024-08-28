from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
import sys
from scene_view import SceneView
from hierarchy import Hierarchy
from properties import Properties
from gameobject import GameObject
from camera import Camera
from control_panel import PainelDeControle

class GameEngine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Engine 2D")
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.scene_view = SceneView()
        self.hierarchy = Hierarchy(self.scene_view)
        self.properties = Properties(self.scene_view)
        
        self.object_dict = {}
        self.key_pressed = set()

        self.hierarchy.hierarchy_tree.itemClicked.connect(self.update_properties)

        layout = QVBoxLayout()
        
        control_layout = PainelDeControle(self.scene_view, self)
        layout.addLayout(control_layout)
        
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.scene_view)
        main_layout.addWidget(self.hierarchy)
        main_layout.addWidget(self.properties)

        layout.addLayout(main_layout)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Verificando se o root_item já existe
        if not self.hierarchy.root_item:
            # Criando o objeto de jogo root_item como nó raiz
            root_item = GameObject("Cena", position=(100, 100), size=(50, 50), color=(255, 0, 0, 255), rotation=0, scale=1, scene_view=self.scene_view)
            
            # Adicionando o root_item à hierarquia
            self.hierarchy.set_root_item(root_item)
            
            # Adicionando root_item ao dicionário de objetos
            self.object_dict[root_item.name] = root_item

        # Criando outros objetos de jogo
        rect1 = GameObject("Rectangle1", position=(100, 100), size=(50, 50), color=(255, 0, 0, 255), rotation=0, scale=1, scene_view=self.scene_view)
        rect2 = GameObject("Rectangle2", position=(200, 200), size=(70, 30), color=(0, 255, 0, 255), rotation=0, scale=1, scene_view=self.scene_view)
        rect3 = GameObject("Rectangle3", position=(350, 200), size=(70, 30), color=(0, 255, 0, 255), rotation=0, scale=1, scene_view=self.scene_view)

        # Adicionando objetos à cena
        self.scene_view.scene_objects.extend([rect1, rect2, rect3])

        # Adicionando objetos à hierarquia e ao dicionário
        self.add_to_hierarchy_and_dict(rect1)
        self.add_to_hierarchy_and_dict(rect2)
        self.add_to_hierarchy_and_dict(rect3)

    def add_to_hierarchy_and_dict(self, game_object):
        if game_object.name not in self.object_dict:
            self.hierarchy.add_gameobject(game_object)
            self.object_dict[game_object.name] = game_object

    def update_properties(self, item):
        selected_item_text = item.text(0)
        selected_object = self.object_dict.get(selected_item_text)
        if selected_object:
            self.properties.set_selected_object(selected_object)
            self.hierarchy.update_cam(item)

            

    def focus_inicial(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        self.show()

    def add_focus(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        self.show()

    def remove_focus(self):
        self.setWindowFlags(Qt.WindowDoesNotAcceptFocus | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.show()
        
    def keyPressEvent(self, event):
        self.key_pressed.add(event.key())
        self.scene_view.update_scene()

    def keyReleaseEvent(self, event):
        self.key_pressed.discard(event.key())
        self.scene_view.update_scene()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(47, 47, 48))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(47, 47, 48))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(47, 47, 48))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)

    window = GameEngine()
    window.focus_inicial()
    sys.exit(app.exec_())
