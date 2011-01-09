# coding=utf8

import os, sys

sys.path.append(os.path.join(os.getcwd()))

from message import Message
import database

class Email(Message):
    
    def __init__(self, fields):
        """
            Initializes a new Email using a dictionary
            of database fields.
        """
        
        Message.__init__(self, fields)
        
        self.remoteId = fields['intEmailRemoteId']
        self.subject = fields['strEmailSubject']
        self.bodyPlain = fields['strEmailBodyPlainText']
        self.bodyHtml = fields['strEmailBodyHtml']
        if 'strRaw' in fields:
            self.raw = fields['strRaw']
    
def getEmailFromId(messageId):
    
    sql = """
        SELECT
            intMessageId,
            intRemoteId AS intEmailRemoteId,
            strSubject AS strEmailSubject,
            strBodyPlainText AS strEmailBodyPlainText,
            strBodyHtml AS strEmailBodyHtml
        FROM mEmail
        WHERE intMessageId = %s"""
    
    return Email(database.executeOneToDictionary(sql, messageId))
    
def store(messageId, remoteId, subject, bodyPlain, bodyHtml, raw):
    """
        Stores the given email to the database. The message
        should be stored first, to give a messageId.
    """
    
    sql = """
        INSERT INTO mEmail 
            (intMessageId, intRemoteId, strSubject, strBodyPlainText, strBodyHtml, strRaw)
        VALUES (%s, %s, %s, %s, %s, %s)"""
    
    database.execute(sql, (messageId, remoteId, subject, bodyPlain, bodyHtml, raw)).close()