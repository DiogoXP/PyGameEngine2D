import random
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer


class a:
    def __init__(self, name, scene_view):
        self.name = name
        self.scene_view = scene_view
        self.started = False
        self.enabled = True
        self.movement_speed = 5  # Define movement_speed as an attribute
        self.v = 0
        self.h = 0

    def Start(self, game_object, started=True):
        pass

    def Update(self, game_object):
        if self.enabled:
            keys = self.scene_view.key_pressed

            if Qt.Key_Up in keys:
                game_object.position = (game_object.position[0], game_object.position[1] - self.movement_speed)

            if Qt.Key_Down in keys:
                game_object.position = (game_object.position[0], game_object.position[1] + self.movement_speed)

            if Qt.Key_Left in keys:
                game_object.position = (game_object.position[0] - self.movement_speed, game_object.position[1])

            if Qt.Key_Right in keys:
                game_object.position = (game_object.position[0] + self.movement_speed, game_object.position[1])

            if Qt.Key_M in keys:  # Supondo que 'M' é a tecla para mover outro objeto
                # Obtendo outro game object em cena
                target_object = self.scene_view.get_gameobject("Rectangle2")
                if target_object:
                    new_position = (target_object.position[0] + 10, target_object.position[1])
                    target_object.position = new_position
                    target_object.notify_change()
                    print(f"{self.name} moved {target_object.name} to {new_position}")

            self.v = game_object.position[0]