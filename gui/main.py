import os, sys

sys.path.append(os.path.join(os.getcwd()))

from PyQt4.QtGui import QAction, QApplication, QGridLayout, QFrame, QIcon
from PyQt4.QtGui import QLabel, QLineEdit, QListView, QMainWindow, QProgressDialog, QWidget
from PyQt4.QtCore import Qt, SIGNAL, SLOT
from threading import Thread
from loginBox import LoginBox
from gatherData import GatherData
from autoCompleteListBox import AutoCompleteListBox

import contact, message

class MainWindow(QMainWindow):

    def setupMenus(self):
        exit = QAction(QIcon('gui/icons/close.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, SIGNAL('triggered()'), SLOT('close()'))
        
        regatherData = QAction('Regather data', self)
        regatherData.setStatusTip('Regather all data')
        self.connect(regatherData, SIGNAL('triggered()'), self.refetchAll)
    
        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(regatherData)
        file.addAction(exit)
        
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exit)
    
    
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(1100, 800)
        self.setWindowTitle('Owl')
                
        self.status = self.statusBar()
        self.status.showMessage('Ready')
        
        self.setupMenus()
        
        userLabel = QLabel('Contacts')
        messageLabel = QLabel('Messages')
        
        self.userList = AutoCompleteListBox(self, [])
        self.messageList = AutoCompleteListBox(self, [])
        
        frame = QFrame()
        frame.setFrameStyle(QFrame.VLine | QFrame.Raised)
        
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        grid.setColumnStretch(2, 2)
        grid.addWidget(userLabel, 0, 0)
        grid.addWidget(messageLabel, 0, 2)
        
        grid.addWidget(self.userList.getLineEdit(), 1, 0)
        grid.addWidget(self.messageList.getLineEdit(), 1, 2)
        
        grid.addWidget(self.userList.getListBox(), 2, 0)
        grid.addWidget(self.messageList.getListBox(), 2, 2)
        
        grid.addWidget(frame, 0, 1, 3, 1)
                
        centralWidget.setLayout(grid)
        
    def giveCredentials(self, username, password):
        self.username = username
        self.password = password
        
        self.refreshLists()
    
    def refreshLists(self):
        contacts = map(contact.getName, contact.getContacts(self.username))
        contacts.sort()        
        self.userList.replaceList(contacts)
        
        messages = map(message.getName, message.getMessages(self.username, 5000))      
        self.messageList.replaceList(messages)
    
    def createProgressBar(self, maximum):
        self.progress.setMaximum(maximum)
        self.progress.setLabelText('Downloading email 1 of ' + str(maximum))
    
    def updateProgressBar(self, messagesProcessed):
        self.progress.setValue(messagesProcessed)
        self.progress.setLabelText('Downloading email %s of %s...' % (str(messagesProcessed + 1), str(self.progress.maximum())))
        
    def receiveBroadcastOfDownloadProgress(self, messagesProcessed):
        self.emit(SIGNAL('updateProgressBar(PyQt_PyObject)'), messagesProcessed)
    
    def fetchMessagesThread(self):
        gatherData = GatherData(self.username, self.password)
        
        newMessageCount = gatherData.countNewMessages()
        self.emit(SIGNAL('receivedMessageCount(PyQt_PyObject)'), newMessageCount)
        
        gatherData.getNewMessages(self.receiveBroadcastOfDownloadProgress)
        
        self.emit(SIGNAL('refreshLists()'))
        
    def refetchAll(self):
        self.progress = QProgressDialog('Looking for emails...', 'Cancel', 0, 10)
        self.progress.resize(400, 50)
        self.progress.show()
        
        thread = Thread(None, self.fetchMessagesThread, 'Fetch messages')
        
        self.connect(self, SIGNAL('receivedMessageCount(PyQt_PyObject)'), self.createProgressBar)
        self.connect(self, SIGNAL('updateProgressBar(PyQt_PyObject)'), self.updateProgressBar)
        self.connect(self, SIGNAL('refreshLists()'), self.refreshLists)
        
        thread.start()
                

app = QApplication(sys.argv)

main = MainWindow()

def afterLogin(username, password):
    main.giveCredentials(username, password)
    main.show()
    
login = LoginBox(afterLogin)
login.show()

sys.exit(app.exec_())
