# coding=utf8

import os, sys

sys.path.append(os.path.join(os.getcwd()))

from PyQt4.QtGui import QGridLayout, QLabel, QLineEdit, QPushButton, QWidget
from PyQt4.QtCore import Qt, SIGNAL, SLOT

from autoCompleteListBox import AutoCompleteListBox
import contact, message, stringFunctions

class EditContact(QWidget):
    
    def __init__(self, mainWindow, username, contact):
        QWidget.__init__(self)
        self.contact = contact
        self.username = username
        self.mainWindow = mainWindow
        
        self.resize(400, 300)
        self.setWindowTitle('Edit Contact')
        
        self.addressListLabel = QLabel('Addresses')
        self.forenameLabel = QLabel('Forename')
        self.surnameLabel = QLabel('Surname')
        
        addresses = self.contact.getAddresses()
        addresses = [("%s: %s" % (address['enmAddressType'], address['strAddress']), address['strAddress']) for address in addresses]
        self.addresses = AutoCompleteListBox(self, addresses)
        self.forenameLineEdit = QLineEdit()
        self.surnameLineEdit = QLineEdit()
        
        if self.contact.forename:
            self.forenameLineEdit.setText(self.contact.forename)
        
        if self.contact.surname:
            self.surnameLineEdit(self.contact.surname)
        
        saveButton = QPushButton('Save')
        cancelButton = QPushButton('Cancel')
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(self.addressListLabel, 1, 0)
        grid.addWidget(self.forenameLabel, 2, 0)
        grid.addWidget(self.surnameLabel, 3, 0)
        
        grid.addWidget(self.addresses.getLineEdit(), 0, 1, 1, 2)
        grid.addWidget(self.addresses.getListBox(), 1, 1, 1, 2)
        grid.addWidget(self.forenameLineEdit, 2, 1, 1, 2)
        grid.addWidget(self.surnameLineEdit, 3, 1, 1, 2)
        
        grid.addWidget(saveButton, 4, 1)
        grid.addWidget(cancelButton, 4, 2)
        
        self.setLayout(grid)
    
        self.connect(cancelButton, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(saveButton, SIGNAL('clicked()'), self.save)
    
    def save(self):
        self.contact.forename = unicode(self.forenameLineEdit.text())
        self.contact.surname = unicode(self.surnameLineEdit.text())
        contact.updateContact(self.username, self.contact.id, self.contact.forename, self.contact.surname)
        self.mainWindow.userList.replaceList([(unicode(c), c) for c in self.mainWindow.contacts])
        self.close()
