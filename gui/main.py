import sys
from PyQt4 import QtGui, QtCore
from loginBox import LoginBox
from gatherData import GatherData

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.resize(800, 600)
        self.setWindowTitle('Owl')

        exit = QtGui.QAction(QtGui.QIcon('gui/icons/close.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        regatherData = QtGui.QAction('Regather data', self)
        regatherData.setStatusTip('Regather all data')
        self.connect(regatherData, QtCore.SIGNAL('triggered()'), self.refetchAll)
        
        self.status = self.statusBar()
        self.status.showMessage('Ready')
        
        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(regatherData)
        file.addAction(exit)

        toolbar = self.addToolBar('regatherData')
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exit)
    
    def giveCredentials(self, username, password):
        self.username = username
        self.password = password
    
    def refetchAll(self):
        gatherData = GatherData(self.username, self.password)
        gatherData.gatherImap()

app = QtGui.QApplication(sys.argv)

main = MainWindow()

def afterLogin(username, password):
    main.giveCredentials(username, password)
    main.show()
    
login = LoginBox(afterLogin)
login.show()

sys.exit(app.exec_())
