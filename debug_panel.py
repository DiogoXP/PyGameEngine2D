# debug_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QSizePolicy
from PyQt5.QtCore import Qt

class DebugPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Debug Panel")
        
        # Layout principal
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Área de texto para exibição de logs e informações
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(QLabel("Log"))
        layout.addWidget(self.log_area)
        
        # Botão para limpar logs
        clear_button = QPushButton("Clear Logs")
        clear_button.clicked.connect(self.clear_logs)
        layout.addWidget(clear_button)

        # Ajustar a política de tamanho para permitir redimensionamento
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def append_log(self, text):
        """Adiciona uma nova entrada ao painel de depuração."""
        self.log_area.append(text)

    def clear_logs(self):
        """Limpa todas as entradas do painel de depuração."""
        self.log_area.clear()
