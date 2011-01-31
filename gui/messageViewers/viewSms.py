# coding=utf8

import os, sys

sys.path.append(os.path.join(os.getcwd()))

from PyQt4.QtGui import QGridLayout, QTextEdit

from viewMessage import ViewMessage

class ViewSms(ViewMessage):
    
    def __init__(self, db, sms):
        ViewMessage.__init__(self, db, sms)
        self.message = sms
        self.resize(400, 250)
        
        text = QTextEdit(self.message.text)
        text.setReadOnly(True)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(text, 0, 0)
        
        self.mainView.setLayout(grid)