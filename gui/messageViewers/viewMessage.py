# coding=utf8

import os, sys, time

sys.path.append(os.path.join(os.getcwd()))

from PyQt4.QtGui import QGridLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QWidget
from PyQt4.QtCore import Qt, SIGNAL, SLOT

from autoCompleteListBox import AutoCompleteListBox
import contact, message, stringFunctions

class ViewMessage(QWidget):
    
    def __init__(self, message):
        QWidget.__init__(self)
        self.message = message
        self.setWindowTitle(message.summary)
        
        senderLabel = QLabel(u'Sender: ' + unicode(message.sender))
        sentLabel = QLabel('Sent: ' + time.strftime('%Y-%m-%d %H:%M:%S', message.sentDate))
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # To be overridden by child classes.
        self.mainView = QWidget()
        
        grid.addWidget(senderLabel, 0, 0)
        grid.addWidget(sentLabel, 1, 0)
        grid.addWidget(self.mainView, 2, 0)
        
        self.setLayout(grid)