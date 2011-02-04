# coding=utf8

import os, sys

sys.path.append(os.path.join(os.getcwd()))

import time
from message import Message
import encryption, message, settings

class IMConversation(Message):
    
    def __init__(self, db, fields):
        """
            Initializes a new IM conversation using a dictionary
            of database fields.
        """
        
        Message.__init__(self, db, fields)
        
        self.remoteId = fields['strIMRemoteId']
        
        self.entries = []
    
    def getEntries(self, db):
        
        if not self.entries:
            sql = """
                SELECT
                    datSent, intSenderId, strText
                FROM mIMEntry
                WHERE intMessageId = ?
                ORDER BY datSent"""
            
            self.entries = db.executeMany(sql, self.id)
            
            for entry in self.entries:
                entry['datSent'] = time.strptime(entry['datSent'], '%Y-%m-%d %H:%M:%S')
            
        return self.entries
    
def getIMConversationFromId(db, messageId):
    
    sql = """
        SELECT
            i.intMessageId,
            i.strRemoteId AS strIMRemoteId,
            a.strType AS strMessageType
        FROM mIMConversation i
            INNER JOIN mMessage m ON m.intId = i.intMessageId
            INNER JOIN aAccount a ON a.intId = m.intAccountId
        WHERE i.intMessageId = ?"""
    
    return IMConversation(db, db.executeOne(sql, messageId))
    
def store(db, messageId, remoteId):
    """
        Stores the given IM conversation to the database. The message
        should be stored first, to give a messageId.
    """
    
    sql = """
        INSERT INTO mIMConversation 
            (intMessageId, strRemoteId)
        VALUES (?, ?)"""
    
    db.executeNone(sql, (messageId, remoteId))

def addEntry(db, messageId, date, senderId, text):
    
    sql = """
        INSERT INTO mIMEntry (intMessageId, datSent, intSenderId, strText)
        VALUES (?, ?, ?, ?)"""
    
    db.executeNone(sql, (messageId, date, senderId, text))