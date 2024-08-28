from PyQt5.QtWidgets import (
    QCheckBox, QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QListWidget, QLabel, QHBoxLayout, 
    QPushButton, QMessageBox
)

from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QMessageBox

class PainelDeControle(QHBoxLayout):
    def __init__(self, scene_view, game_engine, parent=None):
        super().__init__(parent)
        self.scene_view = scene_view
        self.game_engine = game_engine  # Referência à instância de GameEngine.

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_simulation)
        self.addWidget(self.start_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_simulation)
        self.addWidget(self.pause_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.addWidget(self.stop_button)

    def start_simulation(self):
        try:
            self.scene_view.start()
            
        except Exception as e:
            QMessageBox.critical(self.parentWidget(), "Erro", f"Ocorreu um erro ao iniciar a simulação: {e}")
            print(f"Erro: {e}")

    def pause_simulation(self):
        self.scene_view.pause()
        

    def stop_simulation(self):
        self.scene_view.stop()
        

