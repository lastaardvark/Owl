import os, sys
from PyQt4 import QtGui, QtCore

sys.path.append(os.path.join(os.getcwd()))

import login

class LoginBox(QtGui.QWidget):
        
    def __init__(self, afterLogin):
        QtGui.QMainWindow.__init__(self)
        self.afterLogin = afterLogin
        self.setFixedSize(400, 150)
        self.setWindowTitle('Login')
        
        userLabel = QtGui.QLabel('Username: ')
        passwordLabel = QtGui.QLabel('Password: ')
        
        self.userTextBox = QtGui.QLineEdit()
        self.passwordTextBox = QtGui.QLineEdit()
        self.passwordTextBox.setEchoMode(QtGui.QLineEdit.Password)
        self.message = QtGui.QLabel('')
        
        okButton = QtGui.QPushButton('OK')
        cancelButton = QtGui.QPushButton('Cancel')
        
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(userLabel, 0, 0)
        grid.addWidget(passwordLabel, 1, 0)
        grid.addWidget(self.userTextBox, 0, 1, 1, 2)
        grid.addWidget(self.passwordTextBox, 1, 1, 1, 2)
        grid.addWidget(okButton, 2, 1)
        grid.addWidget(cancelButton, 2, 2)
        grid.addWidget(self.message, 3, 0, 1, 3)
        
        self.setLayout(grid)
        
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), QtCore.SLOT('close()'))
        self.connect(okButton, QtCore.SIGNAL('clicked()'), self.onLoginButton)
        self.connect(self.userTextBox, QtCore.SIGNAL('returnPressed()'), self.passwordTextBox, QtCore.SLOT('setFocus()'))
        self.connect(self.passwordTextBox, QtCore.SIGNAL('returnPressed()'), self.onLoginButton)
    
    def onLoginButton(self):
        
        if login.checkLogin(self.userTextBox.text(), self.passwordTextBox.text()):
            self.afterLogin(self.userTextBox.text(), self.passwordTextBox.text())
            self.hide()
        else:
            self.message.setText('Sorry, your username or password was incorrect.')
            self.userTextBox.setFocus()