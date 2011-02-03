# coding=utf8

import os, sys

sys.path.append(os.path.join(os.getcwd()))

import time
from PyQt4.QtGui import QGridLayout, QLabel, QTextEdit

import contact
from viewMessage import ViewMessage

class ViewConversation(ViewMessage):
    
    def __init__(self, db, conversation):
        ViewMessage.__init__(self, db, conversation)
        self.message = conversation
        self.message.getEntries(db)
        self.resize(800, 700)
        self.nextColour = None
        
        senders = {}
        
        body = QTextEdit()
        for entry in self.message.entries:
            
            senderId = entry['intSenderId']
            if senderId in senders:
                sender, colour = senders[senderId]
            else:
                sender = contact.getContactFromId(db, senderId)
                colour = self.getNextColour()
                senders[senderId] = (sender, colour)
            
            sender = u"<b style='color: " + unicode(colour) + u"'>" + unicode(sender) + u'</b>: '
            sent = u'<i>' + unicode(entry['datSent']) + u'</i>:'
            
            row = sender + sent + u'<br/>' + entry['strText'] + u'<br/>'
            
            row += u"<div style='height:20px; clear: both'></div>" 
            
            body.insertHtml(row)
        
        participants = u'Participants: '
        
        for id in senders:
            participants += unicode(senders[id][0]) + u', '
        
        self.senderLabel.setText(participants[:-2])
        
        body.setReadOnly(True)
        self.recipientsWidget.hide()
        
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(body, 0, 0)
        
        self.mainView.setLayout(grid)
        
    def getNextColour(self):
        
        if not self.nextColour:
            self.nextColour = '#0000CC'
        elif self.nextColour ==  '#0000CC':
            self.nextColour = '#40CC00'
        elif self.nextColour ==  '#40CC00':
            self.nextColour = '#CC4000'
        elif self.nextColour ==  '#CC4000':
            self.nextColour = '#404000'
        elif self.nextColour ==  '#404000':
            self.nextColour = '#004040'
        else:
            self.nextColour = '#000000'
            
        return self.nextColour
        