from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import gluOrtho2D
from copy import deepcopy

class Camera:
    def __init__(self, name, position=(0, 0), size=(100, 100), rotation=0, fov=60, scene_view=None):
        self.name = name
        self.position = list(position)
        self.size = list(size)
        self.rotation = rotation
        self.fov = fov
        self.scene_view = scene_view
        
        self.scripts = []
        self.parent = None
        self.children = []
        self.started = False
        self.active = True
        
        self.store_original_state()
    
    def reset(self):
        self.position = deepcopy(self.original_position)
        self.size = deepcopy(self.original_size)
        self.rotation = deepcopy(self.original_rotation)
        self.fov = deepcopy(self.original_fov)
    
    def set_state(self, state):
        self.position = list(state.get("position", self.position))
        self.size = list(state.get("size", self.size))
        self.rotation = state.get("rotation", self.rotation)
        self.fov = state.get("fov", self.fov)
    
    def store_original_state(self):
        self.original_position = deepcopy(self.position)
        self.original_rotation = deepcopy(self.rotation)
        self.original_size = deepcopy(self.size)
        self.original_fov = deepcopy(self.fov)
    
    def apply_view(self, width, height):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(-width / 2, width / 2, height / 2, -height / 2)  # Invert the y-axis
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self._apply_transformations(width, height)
    
    def _apply_transformations(self, width, height):
        glTranslatef(-self.position[0] + width / 2, self.position[1] - height / 2, 0)
        glRotatef(self.rotation, 0, 0, 1)
        glScalef(self.size[0] / 100.0, self.size[1] / 100.0, 1)
    
    def start_scripts(self):
        for script in self.scripts:
            if not script.started:
                script.Start(self)
                script.started = True
    
    def add_script(self, script):
        if script not in self.scripts:
            self.scripts.append(script)
    
    def remove_script(self, script):
        if script in self.scripts:
            self.scripts.remove(script)
            
    def VoidUpdate(self):
        if self.active:
            for script in self.scripts:
                try:
                    script.Update(self)
                except Exception as e:
                    print(f"Error in script {script.name}: {e}")
    
    def set_parent(self, parent):
        self.parent = parent
    
    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)
            child.set_parent(self)
    
    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.set_parent(None)
    
    def set_position(self, new_position):
        delta_x = new_position[0] - self.position[0]
        delta_y = new_position[1] - self.position[1]
        self.position = list(new_position)
        self._update_children_position(delta_x, delta_y)
    
    def _update_children_position(self, delta_x, delta_y):
        for child in self.children:
            new_child_position = (child.position[0] + delta_x, child.position[1] + delta_y)
            child.set_position(new_child_position)
    
    def move(self, delta_x, delta_y):
        self.set_position((self.position[0] + delta_x, self.position[1] + delta_y))
    
    def rotate(self, delta_angle):
        self.rotation += delta_angle
    
    def zoom(self, factor):
        self.fov *= factor
        self.size = [self.size[0] * factor, self.size[1] * factor]
