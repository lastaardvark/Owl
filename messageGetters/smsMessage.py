# coding=utf8

import os, sys

sys.path.append(os.path.join(os.getcwd()))

from message import Message
import database, encryption, message, settings

class Sms(Message):
    
    def __init__(self, fields):
        """
            Initializes a new Sms using a dictionary
            of database fields.
        """
        
        Message.__init__(self, fields)
        
        encryptionKey = settings.settings['userDataEncryptionSalt'] + message._password
        
        self.remoteId = fields['intSmsRemoteId']
        
        self.text = fields['strSmsText']
        
    
def getSmsFromId(messageId):
    
    sql = """
        SELECT
            s.intMessageId,
            s.intRemoteId AS intSmsRemoteId,
            s.strText AS strSmsText,
            a.enmType AS strMessageType
        FROM mSms s
            INNER JOIN mMessage m ON m.intId = s.intMessageId
            INNER JOIN aAccount a ON a.intId = m.intAccountId
        WHERE s.intMessageId = %s"""
    
    return Sms(database.executeOneToDictionary(sql, messageId))
    
def store(messageId, remoteId, text):
    """
        Stores the given SMS message to the database. The message
        should be stored first, to give a messageId.
    """
    
    sql = """
        INSERT INTO mSms 
            (intMessageId, intRemoteId, strText)
        VALUES (%s, %s, %s)"""
    
    database.execute(sql, (messageId, remoteId, text)).close()