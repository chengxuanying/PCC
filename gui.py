import sys
import os
from PyQt5.QtWidgets import (QWidget, QLabel, QMessageBox,
                             QTextEdit, QGridLayout, QApplication, QPushButton)


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        code = QLabel('Code')
        asm = QLabel('ASM')
        input = QLabel('Input')
        output = QLabel('Output')

        codeEdit = QTextEdit()
        asmEdit = QTextEdit()
        inputEdit = QTextEdit()
        outputEdit = QTextEdit()
        self.codeEdit = codeEdit
        self.asmEdit = asmEdit
        self.inputEdit = inputEdit
        self.outputEdit = outputEdit

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(code, 1, 0)
        grid.addWidget(codeEdit, 2, 0)

        grid.addWidget(asm, 1, 1)
        grid.addWidget(asmEdit, 2, 1)

        grid.addWidget(input, 1, 2)
        grid.addWidget(inputEdit, 2, 2)

        grid.addWidget(output, 1, 3)
        grid.addWidget(outputEdit, 2, 3)

        compile_btn = QPushButton('compile')
        grid.addWidget(compile_btn, 3, 0)
        compile_btn.clicked.connect(self.onClick)

        compile_btn2 = QPushButton('run')
        grid.addWidget(compile_btn2, 3, 1)
        compile_btn2.clicked.connect(self.onClick2)

        self.setLayout(grid)

        self.setGeometry(200, 50, 850, 600)
        self.setWindowTitle('PCC x64')
        self.show()

        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        path = e.mimeData().text().replace('file:///', '/')
        with open(path, 'r') as f:
            self.codeEdit.setPlainText(f.read())

        self.path = path

    def onClick(self):

        src = self.codeEdit.toPlainText()

        self.path = 'temp.c'
        with open(self.path, 'w+') as f:
            f.write(src)

        r = os.popen('python3 pcc.py {}'.format(self.path))
        text = r.read()
        r.close()

        if text == '':
            QMessageBox.information(self, "success", "well done!")
            with open(self.path.replace('.c', '.s'), 'r') as f:
                self.asmEdit.setPlainText(f.read())
        else:
            QMessageBox.warning(self, "error", text)

    def onClick2(self):

        with open('temp.in', 'w+') as f:
            f.write(self.inputEdit.toPlainText())

        r = os.popen('./temp < temp.in'.format(self.path))
        text = r.read()
        r.close()

        self.outputEdit.setPlainText(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
