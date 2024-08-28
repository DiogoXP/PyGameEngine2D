# inputs.py

class InputHandler:
    def __init__(self):
        pass

    def handle_pyqt_input(self, qt_event):
        key = qt_event.key()
        key_name = chr(key) if key < 256 else str(key)
        print(f"PyQt5 key pressed: {key_name}")
