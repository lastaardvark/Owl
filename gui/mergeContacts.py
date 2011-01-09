# coding=utf8

import os, sys

sys.path.append(os.path.join(os.getcwd()))

from PyQt4.QtGui import QGridLayout, QPushButton, QDialog

from autoCompleteListBox import AutoCompleteListBox
import contact

class MergeDialog(QDialog):
    
    def __init__(self, contacts):
        """
            This dialog box asks the user whether they really would like to merge
            the given list of contacts. If they agree, the merge is performed.
        """
    	
        QDialog.__init__(self)
        self.contacts = contacts
        
        self.resize(250, 60)
        self.setWindowTitle('Merge Contacts?')
        self.setModal(True)
        self.setSizeGripEnabled(False)
                
        okButton = QPushButton('Merge')
        cancelButton = QPushButton('Cancel')
        
        cancelButton.clicked.connect(self.reject)
        okButton.clicked.connect(self.makeMerge)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(okButton, 0, 0)
        grid.addWidget(cancelButton, 0, 1)
        
        self.setLayout(grid)
        
    def makeMerge(self):
        """
            Called when the user has agreed to merge. Perform
            the merge, and declare that the dialog box was accepted.
        """
        
        contact.mergeContacts(self.contacts)
        self.accept()