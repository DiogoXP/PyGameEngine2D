from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GLUT import *

class SceneView(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 250)
        self.scene_objects = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.running = False
        self.key_pressed = set()
        self.active_camera = None

        self.setFocusPolicy(Qt.StrongFocus)

    def start(self):
        if not self.running:
            self.running = True
            self.timer.start(16)  # Aproximadamente 60 FPS
            print("Simulation started")

    def pause(self):
        if self.running:
            self.running = False
            self.timer.stop()
            print("Simulation paused")

    def stop(self):
        if self.running:
            self.running = False
            self.timer.stop()
            self.reset_scene()
            self.repaint()
            print("Simulation stopped")

    def reset_scene(self):
        for obj in self.scene_objects:
            obj.reset()
        self.repaint()

    def initializeGL(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.15, 0.15, 0.15, 1.0)

        for obj in self.scene_objects:
            if hasattr(obj, 'initialize_texture'):
                obj.initialize_texture()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        if self.active_camera:
            self.active_camera.apply_view(self.width(), self.height())

        objects_with_layer = [obj for obj in self.scene_objects if hasattr(obj, 'layer')]
        objects_without_layer = [obj for obj in self.scene_objects if not hasattr(obj, 'layer')]

        sorted_objects = sorted(objects_with_layer, key=lambda o: o.layer) + objects_without_layer

        for obj in sorted_objects:
            if hasattr(obj, 'draw'):
                obj.draw()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def update_scene(self):
        if self.running:
            for obj in self.scene_objects:
                obj.VoidUpdate()
            self.update()

    def keyPressEvent(self, event):
        self.key_pressed.add(event.key())
        self.update()

    def keyReleaseEvent(self, event):
        self.key_pressed.discard(event.key())
        self.update()

    def add_game_object(self, game_object):
        self.scene_objects.append(game_object)
        if hasattr(game_object, 'initialize_texture'):
            game_object.initialize_texture()
        self.update()

    def set_active_camera(self, camera):
        self.active_camera = camera
        self.update()

    def get_gameobject(self, name):
        for obj in self.scene_objects:
            if obj.name == name:
                return obj
        return None
