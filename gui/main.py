# coding=utf8

import os, sys

sys.path.append(os.path.join(os.getcwd()))

from PyQt4.QtGui import QAbstractItemView, QAction, QApplication, QGridLayout, QFrame, QIcon
from PyQt4.QtGui import QLabel, QLineEdit, QListView, QMainWindow, QProgressDialog, QPushButton
from PyQt4.QtGui import QWidget
from PyQt4.QtCore import Qt, SIGNAL, SLOT
from threading import Thread
from loginBox import LoginBox
from editContact import EditContact
from gatherData import GatherData
from autoCompleteListBox import AutoCompleteListBox

import contact, message, stringFunctions

class MainWindow(QMainWindow):

    def setupMenus(self):
        """
            Constructs menus and toolbars
        """
        
        exit = QAction(QIcon('gui/icons/close.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, SIGNAL('triggered()'), SLOT('close()'))
        
        regatherData = QAction('Regather data', self)
        regatherData.setStatusTip('Regather all data')
        self.connect(regatherData, SIGNAL('triggered()'), self.downloadNewMessages)
    
        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(regatherData)
        file.addAction(exit)
        
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exit)
    
    
    def __init__(self):
        """
            Initialises the main window of the application.
        """
        
        QMainWindow.__init__(self)
        self.setWindowTitle('Owl')
        #self.resize()
        self.setGeometry(10, 10, 1100, 800)
        
        self.status = self.statusBar()
        self.status.showMessage('Ready')
        
        self.setupMenus()
        
        userLabel = QLabel('Contacts')
        messageLabel = QLabel('Messages')
        
        self.userList = AutoCompleteListBox(self, [])
        self.messageList = AutoCompleteListBox(self, [])
        
        box = self.userList.getListBox()
        box.setSelectionMode(QAbstractItemView.ExtendedSelection)
        box.doubleClicked.connect(self.showEditContact)
        box.clicked.connect(self.hideOrShowMergeButton)
        
        frame = QFrame()
        frame.setFrameStyle(QFrame.VLine | QFrame.Raised)
        
        self.mergeButton = QPushButton('Merge')
        self.mergeButton.setEnabled(False)
        
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
        
        grid.addWidget(self.mergeButton, 3, 0)
                
        centralWidget.setLayout(grid)
        
    def giveCredentials(self, username, password):
        """
            This happens once the user has successfully logged in. We store
            the username and password for future reference, and refresh the
            contacts and messages listboxes.
        """
        
        self.username = username
        self.password = password
        
        self.refreshLists()
    
    def refreshListsLocally(self):
        """
            Put the contents of self.contacts and self.messages
            back into the list boxes. Used if a contact or message
            has been changed locally.
        """
        
        self.contacts = sorted(self.contacts, key = lambda contact: unicode(contact))
        self.userList.replaceList([(unicode(c), c) for c in self.contacts])
        self.messageList.replaceList([(unicode(m), m) for m in self.messages])
        
        
    def refreshLists(self):
        """
            Retrieve up-to-date lists of contacts and messages from the database,
            and put them in the relevant list boxes.
        """
        
        self.contacts = contact.getContacts(self.username)        
        self.messages = message.getMessages(self.username, 5000)
        
        self.refreshListsLocally()
    
    def setProgressBarMaximum(self, maximum):
        """
            We call this when we know how many messages to download.
            It sets the maximum of the progress bar, and changes the label text.
        """
        
        self.progress.setMaximum(maximum)
        self.progress.setLabelText('Downloading email 1 of ' + stringFunctions.formatInt(maximum))
    
    def updateProgressBar(self, messagesProcessed):
        """
            We call this when we’ve downloaded a message. We advance the bar’s progress,
            and update the label text. 
        """
            
        self.progress.setValue(messagesProcessed)
        self.progress.setLabelText('Downloading email %s of %s...' % \
            (stringFunctions.formatInt(messagesProcessed + 1), stringFunctions.formatInt(self.progress.maximum())))
        
    def receiveBroadcastOfDownloadProgress(self, messagesProcessed):
        """
            This method is called from the thread doing the downlaoding.
            It emits a signal, triggering the progress bar to be updated.
        """
        self.emit(SIGNAL('updateProgressBar(PyQt_PyObject)'), messagesProcessed)
    
    def cancelMessageRetrieval(self):
        """
            Stop downloading more messages.
        """
        
        self.gatherData.stop()
    
    def fetchMessagesThread(self):
        """
            This is the main method of the thread to download messages.
            It first determines how many messages there are to download, and
            emits a signal to update the GUI. It then downloads the messages
            and emits a signal to refresh the lists.
        """
        
        self.gatherData = GatherData(self.username, self.password)
        
        newMessageCount = self.gatherData.countNewMessages()
        self.emit(SIGNAL('receivedMessageCount(PyQt_PyObject)'), newMessageCount)
        
        self.gatherData.getNewMessages(self.receiveBroadcastOfDownloadProgress)
        
        self.emit(SIGNAL('refreshLists()'))
        
    def downloadNewMessages(self):
        """
            Starts a thread that downloads all the new messages for the user’s
            accounts
        """
        
        self.progress = QProgressDialog('Looking for emails...', 'Cancel', 0, 10)
        self.progress.resize(400, 50)
        self.progress.show()
        
        thread = Thread(None, self.fetchMessagesThread, 'Fetch messages')
        
        self.connect(self, SIGNAL('receivedMessageCount(PyQt_PyObject)'), self.setProgressBarMaximum)
        self.connect(self, SIGNAL('updateProgressBar(PyQt_PyObject)'), self.updateProgressBar)
        self.connect(self, SIGNAL('refreshLists()'), self.refreshLists)
        self.connect(self.progress, SIGNAL('canceled()'), self.cancelMessageRetrieval) 
        
        thread.start()
    
    def showEditContact(self):
    	"""
    		If a single contact is selected, opens the Edit Contact screen for that contact.
    	"""
    	
        contacts = self.userList.getSelectedItems()
        if len(contacts) == 1:
            editContact = EditContact(self, self.username, contacts[0])
            editContact.show()
	
    def hideOrShowMergeButton(self):
		self.mergeButton.setEnabled(len(self.userList.getSelectedItems()) > 1)
			
app = QApplication(sys.argv)

main = MainWindow()

def afterLogin(username, password):
    """
        This is called immediately after the user has successfully logged in.
        We show the main screen, and supply it with the user’s credentials.
    """
    main.giveCredentials(username, password)
    main.show()
    
login = LoginBox(afterLogin)
login.show()

sys.exit(app.exec_())
