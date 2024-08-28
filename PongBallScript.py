import random
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer


class PongBallScript:
    def __init__(self, name, scene_view):
        self.name = name
        self.scene_view = scene_view
        self.started = False
        self.enabled = True
        self.velocity = [random.choice([-5, 5]), random.choice([-5, 5])]  # Velocidade inicial aleatória

    def Start(self, game_object, started=True):
        self.started = started
        if started:
            self.game_object = game_object
            print(f"{self.name} started with initial position {self.game_object.position}")

    def Update(self, game_object):
        if self.enabled:
            self.move_ball(game_object)

    def move_ball(self, game_object):
        # Atualize a posição da bola
        new_position = (
            game_object.position[0] + self.velocity[0],
            game_object.position[1] + self.velocity[1]
        )

        # Verifique colisão com as bordas
        if new_position[0] <= 0 or new_position[0] >= self.scene_view.width() - game_object.size[0]:
            self.velocity[0] = -self.velocity[0]  # Inverta a direção no eixo X

        if new_position[1] <= 0 or new_position[1] >= self.scene_view.height() - game_object.size[1]:
            self.velocity[1] = -self.velocity[1]  # Inverta a direção no eixo Y

        # Verifique colisão com outros game objects
        for obj in self.scene_view.scene_objects:
            if obj != game_object and self.check_collision(new_position, game_object.size, obj):
                self.handle_collision(obj)

        # Atualize a posição do game object
        game_object.position = (
            game_object.position[0] + self.velocity[0],
            game_object.position[1] + self.velocity[1]
        )
        game_object.notify_change()

    def check_collision(self, new_position, size, other_obj):
        # Verifique se há interseção entre os retângulos da bola e do outro objeto
        left1, top1, right1, bottom1 = new_position[0], new_position[1], new_position[0] + size[0], new_position[1] + size[1]
        left2, top2, right2, bottom2 = other_obj.position[0], other_obj.position[1], other_obj.position[0] + other_obj.size[0], other_obj.position[1] + other_obj.size[1]

        return not (right1 <= left2 or right2 <= left1 or bottom1 <= top2 or bottom2 <= top1)

    def handle_collision(self, other_obj):
        # Inverta a direção da bola ao colidir com outro objeto
        self.velocity[0] = -self.velocity[0]
        self.velocity[1] = -self.velocity[1]
        print(f"Collision with {other_obj.name}")

# Exemplo de uso:
# pong_ball_script = PongBallScript("PongBall", scene_view)
# pong_ball_script.Start(game_object)
# No loop de atualização, chame pong_ball_script.Update(game_object)
