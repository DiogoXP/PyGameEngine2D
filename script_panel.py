from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGroupBox, QFormLayout, QLabel, QLineEdit, QCheckBox,
    QListWidget, QListWidgetItem, QHBoxLayout, QSpacerItem, QSizePolicy, QPushButton, QDialog
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from scriptTemplate import ScriptTemplate
from scriptEditor import ScriptEditor
from scene_view import SceneView
import importlib.util
import os

class VariablePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface do usuário para o painel de variáveis."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        self.variable_group = QGroupBox("Variables")
        self.variable_list = QFormLayout()
        self.variable_group.setLayout(self.variable_list)

        self.scroll_area.setWidget(self.variable_group)

        self.setStyleSheet("""
            QGroupBox {
                font: bold;
                border: 1px solid gray;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
            QLabel, QLineEdit, QCheckBox {
                font-size: 14px;
            }
        """)

    def update_variables(self, script):
        """Atualiza os editores de variáveis com base no script fornecido."""
        self.clear_layout(self.variable_list)
        if script:
            for var_name, var_value in vars(script).items():
                if var_name not in ['name', 'scene_view', 'started', 'enabled']:
                    self.add_variable_editor(var_name, var_value, script)

    def add_variable_editor(self, var_name, var_value, script):
        """Adiciona um editor de variável ao painel."""
        widget = QCheckBox() if isinstance(var_value, bool) else QLineEdit()
        if isinstance(widget, QCheckBox):
            widget.setChecked(var_value)
            widget.stateChanged.connect(lambda state, v=var_name: self.update_script_variable(script, v, state == Qt.Checked, bool))
        else:
            widget.setText(str(var_value))
            widget.textChanged.connect(lambda value, v=var_name, t=type(var_value): self.update_script_variable(script, v, value, t))

        self.variable_list.addRow(QLabel(var_name), widget)

    def update_script_variable(self, script, var_name, value, value_type):
        """Atualiza a variável do script com o novo valor."""
        try:
            if value_type == bool:
                value = value.lower() in ('true', '1', 'yes') if isinstance(value, str) else value
            elif value_type == int:
                value = int(value)
            elif value_type == float:
                value = float(value)
            setattr(script, var_name, value)
            updated_value = getattr(script, var_name)
            print(f"Updated script variable {var_name} to {updated_value} of type {type(updated_value)}")
        except ValueError as e:
            print(f"Error updating variable {var_name}: {e}")

    def clear_layout(self, layout):
        """Limpa todos os itens do layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.clear_layout(item.layout())


class ScriptPanel(QWidget):
    def __init__(self, scene_view):
        super().__init__()
        self.scene_view = scene_view
        self.selected_object = None
        self.script_editor = None

        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        """Configura a interface do usuário para o painel de scripts."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        script_group = QGroupBox("Scripts")
        script_layout = QVBoxLayout()
        script_layout.setContentsMargins(10, 10, 10, 10)
        script_layout.setSpacing(10)

        self.script_list = QListWidget()
        self.script_list.itemClicked.connect(self.on_script_selected)
        self.script_input = QLineEdit()
        self.script_input.setPlaceholderText("Enter script name")

        add_script_layout = QHBoxLayout()
        self.add_script_button = QPushButton("Add Script")
        self.add_script_button.setIcon(QIcon.fromTheme("document-new"))
        self.remove_script_button = QPushButton("Remove Script")
        self.remove_script_button.setIcon(QIcon.fromTheme("edit-delete"))
        self.edit_script_button = QPushButton("Edit Script")
        self.edit_script_button.setIcon(QIcon.fromTheme("document-edit"))

        add_script_layout.addWidget(self.add_script_button)
        add_script_layout.addWidget(self.remove_script_button)
        add_script_layout.addWidget(self.edit_script_button)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(QVBoxLayout())
        scroll_content.layout().addWidget(self.script_list)
        scroll_area.setWidget(scroll_content)

        script_layout.addWidget(scroll_area)
        script_layout.addWidget(self.script_input)
        script_layout.addLayout(add_script_layout)

        script_group.setLayout(script_layout)
        layout.addWidget(script_group)

        self.add_script_button.clicked.connect(self.add_new_script)
        self.remove_script_button.clicked.connect(self.remove_script)
        self.edit_script_button.clicked.connect(self.edit_script)

        self.variable_panel = VariablePanel()
        layout.addWidget(self.variable_panel)

    def setup_timer(self):
        """Configura o temporizador para atualizar o painel de variáveis periodicamente."""
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.refresh_variable_panel)
        self.update_timer.start(100)  # Atualiza a cada 100 ms

    def set_selected_object(self, selected_object):
        """Define o objeto selecionado e atualiza a lista de scripts."""
        self.selected_object = selected_object
        if self.selected_object:
            self.update_script_list()

    def update_script_list(self):
        """Atualiza a lista de scripts exibida."""
        self.script_list.clear()
        if self.selected_object:
            for script in self.selected_object.scripts:
                item = QListWidgetItem(script.name)
                widget = QWidget()
                item_layout = QHBoxLayout()
                item_layout.setContentsMargins(0, 0, 0, 0)
                item_layout.setSpacing(5)
                checkbox = QCheckBox()
                checkbox.setChecked(script.enabled)
                checkbox.stateChanged.connect(lambda state, s=script: self.toggle_script(state, s))
                item_layout.addWidget(checkbox)
                item_layout.addWidget(QLabel(script.name))
                item_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
                widget.setLayout(item_layout)
                item.setSizeHint(widget.sizeHint())
                self.script_list.addItem(item)
                self.script_list.setItemWidget(item, widget)

    def on_script_selected(self, item):
        """Atualiza o painel de variáveis quando um script é selecionado."""
        script_name = item.text()
        script = next((s for s in self.selected_object.scripts if s.name == script_name), None)
        if script:
            self.variable_panel.update_variables(script)

    def refresh_variable_panel(self):
        """Atualiza o painel de variáveis se o cenário estiver em execução."""
        if self.scene_view.running:
            selected_item = self.script_list.currentItem()
            if selected_item:
                script_name = selected_item.text()
                script = next((s for s in self.selected_object.scripts if s.name == script_name), None)
                if script:
                    self.variable_panel.update_variables(script)

    def toggle_script(self, state, script):
        """Habilita ou desabilita um script com base no estado do checkbox."""
        script.enabled = (state == Qt.Checked)

    def add_new_script(self):
        """Adiciona um novo script ao objeto selecionado."""
        if self.selected_object and self.script_input.text():
            script_name = self.script_input.text()
            new_script = ScriptTemplate(script_name, self.scene_view)
            self.selected_object.add_script(new_script)
            self.update_script_list()
            self.script_input.clear()
            script_content = self.read_script_template()
            self.save_script(script_name, script_content)

    def read_script_template(self):
        """Lê o conteúdo do template de script."""
        template_path = "./scriptTemplate.py"
        with open(template_path, 'r') as file:
            return file.read()

    def save_script(self, script_name, script_content):
        """Salva o novo script com o conteúdo fornecido."""
        script_content = script_content.replace("ScriptTemplate", script_name)
        with open(f"{script_name}.py", "w") as file:
            file.write(script_content)

    def remove_script(self):
        """Remove os scripts selecionados do objeto selecionado."""
        selected_items = self.script_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            script_name = item.text()
            script_to_remove = next((s for s in self.selected_object.scripts if s.name == script_name), None)
            if script_to_remove:
                self.selected_object.remove_script(script_to_remove)
                self.update_script_list()

    def edit_script(self):
        """Abre o editor para modificar o script selecionado."""
        selected_item = self.script_list.currentItem()
        if not selected_item:
            return
        script_name = selected_item.text()
        script_to_edit = next((s for s in self.selected_object.scripts if s.name == script_name), None)
        if script_to_edit:
            script_file_path = f"{script_name}.py"
            with open(script_file_path, 'r') as file:
                script_content = file.read()
            self.script_editor = ScriptEditor(script_name, script_content, self.save_script_changes)
            self.script_editor.show()

    def save_script_changes(self, script_name, new_script_content):
        """Salva as alterações feitas no script no editor."""
        script_to_save = next((s for s in self.selected_object.scripts if s.name == script_name), None)
        if script_to_save:
            script_to_save.script_content = new_script_content
            script_file_path = f"{script_name}.py"
            with open(script_file_path, 'w') as file:
                file.write(new_script_content)
            print(f"Script '{script_name}' modificado com sucesso.")
            self.reload_script(script_name)

    def reload_script(self, script_name):
        """Recarrega o script após alterações."""
        script_to_reload = next((s for s in self.selected_object.scripts if s.name == script_name), None)
        if script_to_reload:
            script_file_path = f"{script_name}.py"
            try:
                spec = importlib.util.spec_from_file_location(script_name, script_file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                new_script = getattr(module, script_name)(script_name, self.scene_view)
                script_index = self.selected_object.scripts.index(script_to_reload)
                self.selected_object.scripts[script_index] = new_script
                print(f"Script '{script_name}' recarregado com sucesso.")
            except Exception as e:
                print(f"Erro ao recarregar o script '{script_name}': {e}")
