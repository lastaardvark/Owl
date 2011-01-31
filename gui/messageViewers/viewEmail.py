# coding=utf8

import os, sys

sys.path.append(os.path.join(os.getcwd()))

from PyQt4.QtGui import QGridLayout, QLabel, QTextEdit

from viewMessage import ViewMessage

class ViewEmail(ViewMessage):
    
    def __init__(self, email):
        ViewMessage.__init__(self, email)
        self.message = email
        self.resize(600, 700)
        
        subjectLabel = QLabel(u'Subject: ' + self.message.subject)
        
        #bodyLabel = QTextEdit(self.message.bodyPlain)
        body = QTextEdit()
        
        if self.message.bodyHtml:
            print 'html'
            body.insertHtml(self.message.bodyHtml)
        else:
            print 'plain'
            body.insertPlainText(self.message.bodyPlain)
        
        body.textCursor().setPosition(0)
        body.setReadOnly(True)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(subjectLabel, 0, 0)
        grid.addWidget(body, 1, 0)
        
        self.mainView.setLayout(grid)