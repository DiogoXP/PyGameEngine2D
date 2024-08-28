import numpy as np
from PIL import Image
from OpenGL.GL import *
from PyQt5.QtGui import QColor
from copy import deepcopy
from PyQt5.QtCore import QTimer


class GameObject:
    def __init__(self, name, position=(0, 0), size=(50, 50), color=(255, 255, 255, 255), rotation=0, scale=1, scene_view=None, image_path=None):
        self.name = name
        self.position = position
        self.size = size
        self.color = color
        self.rotation = rotation
        self.scale = scale
        self.scene_view = scene_view
        self.texture_id = None
        self.scripts = []
        self.started = False
        self.active = True
        self.image_path = image_path
        self.offset_x = 0
        self.offset_y = 0
        self.tiling_x = 1
        self.tiling_y = 1
        self.overlay_color = QColor(0, 0, 0, 0)
        self.layer = 0

        self.original_position = deepcopy(self.position)
        self.original_size = deepcopy(self.size)
        self.original_color = deepcopy(self.color)
        self.original_rotation = deepcopy(self.rotation)
        self.texture_id = self.texture_id
        self.original_scale = deepcopy(self.scale)
        self.original_image_path = deepcopy(self.image_path)
        self.original_overlay_color = deepcopy(self.overlay_color)
        self.original_layer = deepcopy(self.layer)

        self.parent = None
        self.children = []


    def reset(self):
        self.position = deepcopy(self.original_position)
        self.size = deepcopy(self.original_size)
        self.color = deepcopy(self.original_color)
        self.rotation = deepcopy(self.original_rotation)
        self.scale = deepcopy(self.original_scale)
        self.image_path = deepcopy(self.original_image_path)
        self.overlay_color = deepcopy(self.original_overlay_color)
        self.layer = deepcopy(self.original_layer)
        self.update_image()
        print(f"{self.name} reset to original position {self.original_position}")
    
    def set_parent(self, parent):
        self.parent = parent

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)
            child.set_parent(self)
    
    def remove_parent(self):
        if self.parent:
            self.parent.remove_child(self)
            self.set_parent(None)
            
    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.set_parent(None)

    def set_position(self, new_position):
        delta_x = new_position[0] - self.position[0]
        delta_y = new_position[1] - self.position[1]
        self.position = new_position
        self._update_children_position(delta_x, delta_y)

    def _update_children_position(self, delta_x, delta_y):
        for child in self.children:
            new_child_position = (child.position[0] + delta_x, child.position[1] + delta_y)
            child.set_position(new_child_position)

    def update_position(self, delta):
        new_position = (self.position[0] + delta[0], self.position[1] + delta[1])
        self.set_position(new_position)
        self._update_children_position()
        

    def notify_change(self):
        self.update_image()
        if self.scene_view:
            self.scene_view.update()

    def initialize_texture(self):
        if self.texture_id is None:
            self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        self.update_image()

    def update_image(self):
        if self.texture_id is None:
            return
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        if self.image_path:
            image = Image.open(self.image_path).convert("RGBA")
            image = image.resize((int(self.size[0]), int(self.size[1])))
        else:
            size = (int(self.size[0]), int(self.size[1]))
            color = tuple(map(int, self.color))
            image = Image.new("RGBA", size, color)
        image_data = np.array(image)

        # Apply overlay color with alpha blending
        overlay_color = np.array(self.overlay_color.getRgb())
        overlay_color = overlay_color / 255.0
        overlay_color = np.append(overlay_color[:3], overlay_color[3])
        overlay_image = np.full(image_data.shape, overlay_color)
        blended_image = (image_data * (1 - overlay_color[3]) + overlay_image * overlay_color[3]).astype(np.uint8)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, blended_image)

    def draw(self):
        if self.texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glPushMatrix()
            glTranslatef(self.position[0], self.position[1], 0)
            glRotatef(self.rotation, 0, 0, 1)
            glScalef(self.scale, self.scale, 1)

            offset_x = self.offset_x % self.size[0]
            offset_y = self.offset_y % self.size[1]

            glBegin(GL_QUADS)
            glColor4f(1, 1, 1, 1)
            glTexCoord2f(0 + offset_x / self.size[0], 0 + offset_y / self.size[1])
            glVertex2f(-self.size[0] / 2, -self.size[1] / 2)
            glTexCoord2f(self.tiling_x + offset_x / self.size[0], 0 + offset_y / self.size[1])
            glVertex2f(self.size[0] / 2, -self.size[1] / 2)
            glTexCoord2f(self.tiling_x + offset_x / self.size[0], self.tiling_y + offset_y / self.size[1])
            glVertex2f(self.size[0] / 2, self.size[1] / 2)
            glTexCoord2f(0 + offset_x / self.size[0], self.tiling_y + offset_y / self.size[1])
            glVertex2f(-self.size[0] / 2, self.size[1] / 2)
            glEnd()

            glPopMatrix()
            glDisable(GL_TEXTURE_2D)

    def set_image(self, image_path):
        self.image_path = image_path
        self.update_image()
        self.notify_change()

    def set_overlay_color(self, color):
        self.overlay_color = color
        self.update_image()
        self.notify_change()

    def set_offset(self, offset_x, offset_y):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.notify_change()

    def set_tiling(self, tiling_x, tiling_y):
        self.tiling_x = tiling_x
        self.tiling_y = tiling_y
        self.notify_change()

    def set_layer(self, layer):
        self.layer = layer
        self.notify_change()

    def get_layer(self):
        return self.layer

    def VoidStart(self):
        for script in self.scripts:
            if not script.started:
                script.Start(self)
                script.started = True

    def add_script(self, script):
        self.scripts.append(script)

    def remove_script(self, script):
        if script in self.scripts:
            self.scripts.remove(script)

    def get_state(self):
        return {
            "position": self.position,
            "size": self.size,
            "color": self.color,
            "rotation": self.rotation,
            "scale": self.scale,
            "layer": self.layer
        }

    def set_state(self, state):
        self.position = state.get("position", self.position)
        self.size = state.get("size", self.size)
        self.color = state.get("color", self.color)
        self.rotation = state.get("rotation", self.rotation)
        self.scale = state.get("scale", self.scale)
        self.layer = state.get("layer", self.layer)
        self.update_image()

    def store_original_state(self):
        self.original_position = deepcopy(self.position)
        self.original_size = deepcopy(self.size)
        self.original_color = deepcopy(self.color)
        self.original_rotation = deepcopy(self.rotation)
        self.original_scale = deepcopy(self.scale)
        self.original_layer = deepcopy(self.layer)
        print(f"{self.name} original position stored as {self.original_position}")

    def VoidUpdate(self):
        """Update the GameObject and its children."""
        if self.active:
            # Update the GameObject itself
            for script in self.scripts:
                try:
                    script.Update(self)
                except Exception as e:
                    print(f"Error in script {script.name}: {e}")
            self.update_children()

    def update_children(self):
        """Update all children based on the parent's transformation."""
        for child in self.children:
            delta_x = self.position[0] - self.original_position[0]
            delta_y = self.position[1] - self.original_position[1]
            child.position = (
                child.original_position[0] + delta_x,
                child.original_position[1] + delta_y
            )
            child.VoidUpdate()



    def update_game_objects(self):
        """Update all game objects in the scene."""
        for game_object in self.game_objects:
            game_object.update()
            game_object.draw()
        self.scene_view.update()

    def add_game_object(self, game_object):
        self.game_objects.append(game_object)
        game_object.scene_view = self.scene_view
        game_object.initialize_texture()
        game_object.VoidStart()
