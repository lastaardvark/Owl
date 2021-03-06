# coding=utf8

import os, sys

sys.path.append(os.path.join(os.getcwd()))

from message import Message
import encryption, message, settings

class Email(Message):
    
    def __init__(self, db, fields):
        """
            Initializes a new Email using a dictionary
            of database fields.
        """
        fields['strMessageType'] = 'imap'
        
        Message.__init__(self, db, fields)
        
        encryptionKey = settings.settings['userDataEncryptionSalt'] + message._password
        
        self.remoteId = fields['intEmailRemoteId']
        
        self.subject = fields['strEmailSubject']
        
        self.bodyPlain = fields['strEmailBodyPlainText']
        self.bodyPlain = encryption.decrypt(encryptionKey, self.bodyPlain)
        
        self.bodyHtml = fields['strEmailBodyHtml']
        self.bodyHtml = encryption.decrypt(encryptionKey, self.bodyHtml)
        
        if 'strRaw' in fields:
            self.raw = fields['strRaw']
            self.raw = encryption.decrypt(encryptionKey, self.raw)
        
    
def getEmailFromId(db, messageId):
    
    sql = """
        SELECT
            intMessageId,
            intRemoteId AS intEmailRemoteId,
            strSubject AS strEmailSubject,
            strBodyPlainText AS strEmailBodyPlainText,
            strBodyHtml AS strEmailBodyHtml
        FROM mEmail
        WHERE intMessageId = ?"""
    print messageId
    return Email(db, db.executeOne(sql, messageId))
    
def store(db, messageId, remoteId, subject, bodyPlain, bodyHtml, raw):
    """
        Stores the given email to the database. The message
        should be stored first, to give a messageId.
    """
    
    sql = """
        INSERT INTO mEmail 
            (intMessageId, intRemoteId, strSubject, strBodyPlainText, strBodyHtml, strRaw)
        VALUES (?, ?, ?, ?, ?, ?)"""
    
    db.executeNone(sql, (messageId, remoteId, subject, bodyPlain, bodyHtml, raw))