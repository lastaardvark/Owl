import sys
from PyQt4 import QtGui, QtCore
from loginBox import LoginBox

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.resize(800, 600)
        self.setWindowTitle('Owl')

        exit = QtGui.QAction(QtGui.QIcon('gui/icons/close.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        self.status = self.statusBar()
        self.status.showMessage('Ready')
        
        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(exit)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exit)


app = QtGui.QApplication(sys.argv)

main = MainWindow()

def afterLogin():
    main.show()
    
login = LoginBox(afterLogin)
login.show()

sys.exit(app.exec_())
