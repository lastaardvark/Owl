# coding=utf8

import os, sys

sys.path.append(os.path.join(os.getcwd()))

from PyQt4.QtGui import QAbstractItemView, QAction, QApplication, QGridLayout, QFrame, QIcon
from PyQt4.QtGui import QLabel, QLineEdit, QListView, QMainWindow, QProgressDialog
from PyQt4.QtGui import QPushButton, QWidget
from PyQt4.QtCore import Qt, SIGNAL, SLOT
from threading import Thread
from loginBox import LoginBox
from editContact import EditContact
from gatherData import GatherData
from autoCompleteListBox import AutoCompleteListBox
from messageListBox import MessageListBox
from mergeContacts import MergeDialog
from dialogBox import DialogBox
from multiselectionDialogBox import MultiselectionDialogBox
from messageViewers.viewEmail import ViewEmail
from messageViewers.viewSms import ViewSms
from messageViewers.viewConversation import ViewConversation
from messageGetters import imConversation, emailMessage, smsMessage
from sqlite import Sqlite

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
        
        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        self.getMessagesMenu = file.addMenu('&Get Messages')
        
        file.addAction(exit)
        
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exit)
    
    
    def __init__(self):
        """
            Initialises the main window of the application.
        """
        
        QMainWindow.__init__(self)
        self.setWindowTitle('Owl')
        self.setGeometry(10, 10, 1100, 800)
        
        self.status = self.statusBar()
        self.status.showMessage('Ready')
        
        self.setupMenus()
        
        userLabel = QLabel('Contacts')
        messageLabel = QLabel('Messages')
        
        self.userList = AutoCompleteListBox(self, [])
        self.messageList = MessageListBox(self, [])
        
        box = self.userList.getListBox()
        box.setSelectionMode(QAbstractItemView.ExtendedSelection)
        box.doubleClicked.connect(self.showEditContact)
        box.clicked.connect(self.contactListClicked)
        
        self.messageList.getListBox().doubleClicked.connect(self.showMessage)
        
        frame = QFrame()
        frame.setFrameStyle(QFrame.VLine | QFrame.Raised)
        
        self.mergeButton = QPushButton('Merge')
        self.mergeButton.setEnabled(False)
        self.mergeButton.clicked.connect(self.mergeContacts)
        
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
        message._password = password
        
        self.db = Sqlite(username, True)
        
        self.gatherData = GatherData(self.username, self.password)
        
        self.refreshLists()
        
        self.refreshGetMessagesWindow()
    
    def refreshLists(self):
        """
            Put locally-stored contact and message lists
            back into the list boxes. Used if a contact or message
            has been changed locally.
        """
        
        contacts = sorted(contact.getContacts(self.db), key = lambda contact: unicode(contact))
        messages = sorted(message.getMessages(self.db), key = lambda message: unicode(message))
        self.userList.replaceList([(unicode(c), c) for c in contacts])
        self.messageList.replaceList([(unicode(m), m) for m in messages])
        
    def refreshGetMessagesWindow(self):
        
        self.getMessagesMenu.clear()
        
        self.gatherData.refreshNewMessageCounts(self.db)
        
        messageCounts = self.gatherData.getAllNewMessageCounts()
        
        for count in messageCounts:
            
            action = QAction(count['type'] + '  (' + str(count['number']) + ')', self)
            
            if count['type'] == 'All':
                tip = 'Get all new messages.'
            else:
                tip = 'Get new ' + count['type'] + ' messages.'
            
            action.setStatusTip(tip)
            
            self.getMessagesMenu.addAction(action)
            
            receiver = lambda type=count['type']: self.downloadNewMessages(type)
            
            self.connect(action, SIGNAL('triggered()'), receiver)
            
    
    def updateProgressBar(self, messagesLeft):
        """
            We call this when we’ve downloaded a message. We advance the bar’s progress,
            and update the label text. 
        """
        
        messagesProcessed = self.progress.maximum() - messagesLeft
        self.progress.setValue(messagesProcessed)
        self.progress.setLabelText('Downloading message %s of %s.' % \
            (stringFunctions.formatInt(messagesProcessed + 1), stringFunctions.formatInt(self.progress.maximum())))
            
        if messagesProcessed >= self.progress.maximum():
            self.progress.close()
        
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
    
    def fetchMessagesThread(self, type):
        
        self.gatherData.getNewMessages(self.receiveQuestion, type, self.receiveBroadcastOfDownloadProgress)
        
        self.emit(SIGNAL('refreshLists()'))
    
    def receiveQuestion(self, options, title, text, resultReceiver, multiAnswer = False):
        self.emit(SIGNAL('askUserAQuestion(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)'), \
            options, title, text, resultReceiver, multiAnswer)
    
    def askUserAQuestion(self, options, title, text, resultReceiver, multiAnswer):
        if multiAnswer:        
            self.dialog = MultiselectionDialogBox(options, title, text, resultReceiver)
        else:
            self.dialog = DialogBox(options, title, text, resultReceiver)
    
    def downloadNewMessages(self, messageType):
        """
            Starts a thread that downloads all the new messages for the user’s
            accounts
        """
        
        newMessageCount = self.gatherData.countNewMessages(messageType)
        noun = newMessageCount == 1 and 'message' or 'messages'
        
        self.progress = QProgressDialog(str(newMessageCount) + ' ' + noun + ' to download.', 'Cancel', 0, 10)
        self.progress.resize(400, 50)
        self.progress.setMaximum(newMessageCount)
        self.progress.show()
        
        thread = Thread(target=self.fetchMessagesThread, name='Fetch messages', args=(messageType,))
        
        self.connect(self, SIGNAL('updateProgressBar(PyQt_PyObject)'), self.updateProgressBar)
        self.connect(self, SIGNAL('refreshLists()'), self.refreshLists)
        self.connect(self.progress, SIGNAL('canceled()'), self.cancelMessageRetrieval) 
        self.connect(self, SIGNAL('askUserAQuestion(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)'), self.askUserAQuestion) 
        
        thread.start()
    
    def showEditContact(self):
    	"""
    		If a single contact is selected, opens the Edit Contact screen for that contact.
    	"""
    	
        contacts = self.userList.getSelectedItems()
        if len(contacts) == 1:
            self.editContact = EditContact(self.db, self, self.username, contacts[0])
            self.editContact.show()
	
    def showMessage(self):
    	"""
	        If a message is selected, opens the show message screen for that message.
    	"""
    	
        messages = self.messageList.getSelectedItems()
        
        if len(messages) == 1:
            
            if messages[0].type == 'email':
            
                self.viewMessage = ViewEmail(self.db, emailMessage.getEmailFromId(self.db, messages[0].id))
            
            elif messages[0].type == 'SMS':
            
                self.viewMessage = ViewSms(self.db, smsMessage.getSmsFromId(self.db, messages[0].id))
                
            elif messages[0].type == 'IM':
            
                self.viewMessage = ViewConversation(self.db, imConversation.getIMConversationFromId(self.db, messages[0].id))
                
            self.viewMessage.show()
    
    def contactListClicked(self):
        """
            Enables or disables the merge button, depending on whether or not
            two or more contacts are selected, respectively.
        """
        
        contacts = self.userList.getSelectedItems()
        self.mergeButton.setEnabled(contacts != None and len(contacts) > 1)
        
        if contacts != None and len(contacts) == 1:
            self.messageList.filterByContact(contacts[0])
        else:
            self.messageList.removeFilter()

    def mergeContacts(self):
        """
            Ask the user whether they want to merge the contacts that are selected in the list box.
        """
        self.mergeDialog = MergeDialog(self.db, self.userList.getSelectedItems())
        self.mergeDialog.accepted.connect(self.refreshLists)
        self.mergeDialog.show()
	
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
