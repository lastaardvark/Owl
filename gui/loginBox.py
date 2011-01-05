# coding=utf8

import os, sys
from PyQt4.QtGui import QGridLayout, QLabel, QLineEdit, QPushButton, QWidget
from PyQt4.QtCore import SIGNAL, SLOT

import login, settings

class LoginBox(QWidget):
        
    def __init__(self, afterLogin):
        """
            Initiates a login box. This will contain a username and password box,
            and OK and Cancel buttons.
            
            If the user successfully logs in, this login box will he hidden, and
            the function afterLogin will be called.
        """
        
        QWidget.__init__(self)
        self.afterLogin = afterLogin
        self.setFixedSize(400, 150)
        self.setWindowTitle('Login')
        
        userLabel = QLabel('Username: ')
        passwordLabel = QLabel('Password: ')
        
        self.userTextBox = QLineEdit()
        self.passwordTextBox = QLineEdit()
        self.passwordTextBox.setEchoMode(QLineEdit.Password)
        self.message = QLabel('')
        
        self.userTextBox.setText(settings.settings['tempLogin'])
        self.passwordTextBox.setText(settings.settings['tempPassword'])
        
        okButton = QPushButton('OK')
        cancelButton = QPushButton('Cancel')
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(userLabel, 0, 0)
        grid.addWidget(passwordLabel, 1, 0)
        grid.addWidget(self.userTextBox, 0, 1, 1, 2)
        grid.addWidget(self.passwordTextBox, 1, 1, 1, 2)
        grid.addWidget(okButton, 2, 1)
        grid.addWidget(cancelButton, 2, 2)
        grid.addWidget(self.message, 3, 0, 1, 3)
        
        self.setLayout(grid)
        
        self.connect(cancelButton, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(okButton, SIGNAL('clicked()'), self.onLoginButton)
        self.connect(self.userTextBox, SIGNAL('returnPressed()'), self.passwordTextBox, SLOT('setFocus()'))
        self.connect(self.passwordTextBox, SIGNAL('returnPressed()'), self.onLoginButton)
    
    def onLoginButton(self):
        user = str(self.userTextBox.text())
        password = str(self.passwordTextBox.text())
        if login.checkLogin(user, password):
            self.afterLogin(user, password)
            self.hide()
        else:
            self.message.setText('Sorry, your username or password was incorrect.')
            self.userTextBox.setFocus()