import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import newimagedlg

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.dirty = False
        self.filename = None

        self.messageLabel = QLabel()
        self.messageLabel.setAlignment(Qt.AlignCenter)
        self.messageLabel.setText('居中')
        self.setCentralWidget(self.messageLabel)

        fileNewAction = QAction(QIcon('images/filenew.png'), '&New', self)
        fileNewAction.setShortcut(QKeySequence.New)
        fileNewAction.setToolTip('Create a new message')
        fileNewAction.triggered.connect(self.printMessage)

        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenu.addAction(fileNewAction)
        # 下面用QMetaObject的signal&slot机制实现triggered这个信号与相应槽的连接
        metainfo = QMetaObject()

    def printMessage(self):
        text = 'File/New 菜单'
        self.messageLabel.setText(text)

app = QApplication(sys.argv)
app.setApplicationName('test QMetaObject')
form = MainWindow()
form.show()
app.exec_()
