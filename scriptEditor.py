from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from PyQt5.QtGui import QFont, QColor, QIcon

class ScriptEditor(QDialog):
    def __init__(self, script_name, script_content, save_callback):
        super().__init__()
        self.script_name = script_name
        self.script_content = script_content
        self.save_callback = save_callback

        self.setWindowTitle(f"Edit Script: {script_name}")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.text_edit = QsciScintilla()
        self.setup_editor()
        self.text_edit.setText(script_content)
        layout.addWidget(self.text_edit)

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        save_button = QPushButton("Save")
        save_button.setIcon(QIcon.fromTheme("document-save"))
        save_button.clicked.connect(self.save_script)
        buttons_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setIcon(QIcon.fromTheme("window-close"))
        cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.activateWindow()
        self.raise_()

    def setup_editor(self):
        # Configurar numeração de linhas
        self.text_edit.setMarginsFont(QFont('Courier', 10))
        self.text_edit.setMarginLineNumbers(1, True)
        self.text_edit.setMarginWidth(1, 35)

        # Tema Dark
        self.text_edit.setPaper(QColor('#1e1e1e'))  # Fundo
        self.text_edit.setColor(QColor('#dcdcdc'))  # Texto

        lexer = QsciLexerPython()
        lexer.setDefaultFont(QFont('Courier', 10))

        # Definir cores para o lexer
        lexer.setColor(QColor('#569cd6'), QsciLexerPython.Keyword)       # Palavras-chave
        lexer.setColor(QColor('#d69d85'), QsciLexerPython.ClassName)     # Nome de classes
        lexer.setColor(QColor('#4ec9b0'), QsciLexerPython.Comment)       # Comentários
        lexer.setColor(QColor('#9cdcfe'), QsciLexerPython.DoubleQuotedString)  # Strings
        lexer.setColor(QColor('#9cdcfe'), QsciLexerPython.SingleQuotedString)  # Strings
        lexer.setColor(QColor('#ce9178'), QsciLexerPython.FunctionMethodName)  # Nomes de funções
        lexer.setColor(QColor('#dcdcaa'), QsciLexerPython.Number)        # Números
        lexer.setColor(QColor('#c586c0'), QsciLexerPython.Operator)      # Operadores
        lexer.setColor(QColor('#d7ba7d'), QsciLexerPython.Identifier)    # Identificadores

        self.text_edit.setLexer(lexer)

        # Realce de sintaxe
        self.text_edit.setUtf8(True)

        # Configurar algumas propriedades adicionais
        self.text_edit.setIndentationsUseTabs(False)
        self.text_edit.setTabWidth(4)
        self.text_edit.setIndentationGuides(True)
        self.text_edit.setFolding(QsciScintilla.PlainFoldStyle)
        self.text_edit.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.text_edit.setCaretLineVisible(True)
        self.text_edit.setCaretLineBackgroundColor(QColor('#2a2a2a'))
        self.text_edit.setMarginsBackgroundColor(QColor('#2a2a2a'))
        self.text_edit.setMarginsForegroundColor(QColor('#ffffff'))
        self.text_edit.setEdgeMode(QsciScintilla.EdgeLine)
        self.text_edit.setEdgeColumn(80)
        self.text_edit.setEdgeColor(QColor('#555555'))

    def save_script(self):
        new_content = self.text_edit.text()
        try:
            self.save_callback(self.script_name, new_content)
            self.close()
        except Exception as e:
            error_message = f"Erro ao salvar o script '{self.script_name}':\n{e}"
            print(error_message)
            QMessageBox.critical(self, "Erro ao Salvar Script", error_message)
