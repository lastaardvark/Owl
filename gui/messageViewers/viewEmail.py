# coding=utf8

import os, sys

sys.path.append(os.path.join(os.getcwd()))

from PyQt4.QtGui import QGridLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QWidget
from PyQt4.QtCore import Qt, SIGNAL, SLOT

from viewMessage import ViewMessage

class ViewEmail(ViewMessage):
    
    def __init__(self, email):
        ViewMessage.__init__(self, email)