# coding=utf8

import os, sys

sys.path.append(os.path.join(os.getcwd()))

from PyQt4.QtGui import QGridLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QWidget
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
        
        addresses = self.contact.getAddresses()
        addresses = [("%s: %s" % (address['enmAddressType'], address['strAddress']), address['strAddress']) for address in addresses]
        self.addresses = AutoCompleteListBox(self, addresses)
        self.addresses.getLineEdit().hide()
        
        saveButton = QPushButton('Save')
        cancelButton = QPushButton('Cancel')
        
        self.personRadio = QRadioButton('Contact is a person', self)
        self.companyRadio = QRadioButton('Contact is an organization', self)
        
        self.personWidget = self._getPersonWidget()
        self.companyWidget = self._getCompanyWidget()
        
        self.personRadio.toggled.connect(self.switchToPerson)
        self.companyRadio.toggled.connect(self.switchToCompany)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(self.addressListLabel, 1, 0)
        grid.addWidget(self.addresses.getLineEdit(), 0, 1, 1, 2)
        grid.addWidget(self.addresses.getListBox(), 1, 1, 1, 2)
        
        grid.addWidget(self.personRadio, 2, 1, 1, 2)
        grid.addWidget(self.companyRadio, 3, 1, 1, 2)
        
        grid.addWidget(self.personWidget, 4, 0, 1, 3)
        grid.addWidget(self.companyWidget, 5, 0, 1, 3)
        
        grid.addWidget(saveButton, 7, 1)
        grid.addWidget(cancelButton, 7, 2)
        
        self.setLayout(grid)
        
        if contact.isPerson == True:
            self.personRadio.setChecked(True)
            self.switchToPerson()
        elif contact.isPerson == False:
            self.companyRadio.setChecked(True)
            self.switchToCompany()
        else:
            self.personWidget.hide()
            self.companyWidget.hide()
        
        self.connect(cancelButton, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(saveButton, SIGNAL('clicked()'), self.save)
        
    def _getPersonWidget(self):
        widget = QWidget()
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        self.forenameLabel = QLabel('Forename')
        self.surnameLabel = QLabel('Surname')
        
        self.forenameLineEdit = QLineEdit()
        self.surnameLineEdit = QLineEdit()
        
        if self.contact.forename:
            self.forenameLineEdit.setText(self.contact.forename)
        
        if self.contact.surname:
            self.surnameLineEdit.setText(self.contact.surname)
        
        grid.addWidget(self.forenameLabel, 0, 0)
        grid.addWidget(self.surnameLabel, 1, 0)
        
        grid.addWidget(self.forenameLineEdit, 0, 1)
        grid.addWidget(self.surnameLineEdit, 1, 1)
        
        widget.setLayout(grid)
        
        return widget
        
    def _getCompanyWidget(self):
        widget = QWidget()
        grid = QGridLayout()
        grid.setSpacing(10)
        
        self.companyNameLabel = QLabel('Company Name')
        
        self.companyNameLineEdit = QLineEdit()
        
        if self.contact.companyName:
            self.companyNameLineEdit.setText(self.contact.companyName)
        
        grid.addWidget(self.companyNameLabel, 0, 0)        
        grid.addWidget(self.companyNameLineEdit, 0, 1)
        
        widget.setLayout(grid)
        
        return widget
    
    def switchToPerson(self):
        self.companyWidget.hide()
        self.personWidget.show()
    
    def switchToCompany(self):
        self.personWidget.hide()
        self.companyWidget.show()
        
    def save(self):
        self.contact.forename = unicode(self.forenameLineEdit.text())
        self.contact.surname = unicode(self.surnameLineEdit.text())
        self.contact.companyName = unicode(self.companyNameLineEdit.text())
        
        self.contact.isPerson = self.personRadio.isChecked()
        
        self.contact.update()
        self.mainWindow.refreshListsLocally()
        self.close()
