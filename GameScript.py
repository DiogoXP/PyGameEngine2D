from PyQt5.QtCore import QObject, pyqtSignal

class GameScript(QObject):
    def __init__(self, name, scene_view, game_object):
        super().__init__()
        self.name = name
        self.scene_view = scene_view
        self.game_object = game_object
        self.enabled = True

    def start(self):
        pass

    def update(self):
        pass

    def on_enable(self):
        pass

    def on_disable(self):
        pass

    def enable(self):
        self.enabled = True
        self.on_enable()

    def disable(self):
        self.enabled = False
        self.on_disable()
