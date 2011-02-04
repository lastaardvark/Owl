# coding=utf8

import time

import contact

_password = ''

class Message:
    
    def __init__(self, db, fields):
        """
            Initializes a new Message using a dictionary
            of database fields.
        """
        
        self.id = fields['intMessageId']
        
        if not 'intSenderId' in fields:
            
            sql = """
                SELECT
                    m.intSenderId,
                    m.datHappened,
                    m.strSummary,
                    r.intOnlyRecipient
                FROM mMessage m
                    LEFT JOIN (
                        SELECT intMessageId, MIN(intContactId) AS intOnlyRecipient
                        FROM mRecipient
                        GROUP BY intMessageId
                        HAVING COUNT(*) =1
                    ) r ON r.intMessageId = m.intId
                WHERE intId = ?"""
            
            row = db.executeOne(sql, self.id)
            fields['intSenderId'] = row['intSenderId']
            fields['datHappened'] = row['datHappened']
            fields['strSummary'] = row['strSummary']
        
        self.sender = contact.getContactFromId(db, fields['intSenderId'])
        self.sentDate = time.strptime(fields['datHappened'], '%Y-%m-%d %H:%M:%S')
        self.summary = fields['strSummary'].replace(u'\n', u'')
        if fields['strMessageType'] == 'imap':
            self.type = 'email'
        elif fields['strMessageType'] == 'iPhone SMS':
            self.type = 'SMS'
        elif fields['strMessageType'] == 'IM':
            self.type = 'IM'
        
        if len(self.summary) > 77:
            self.summary = self.summary[:77] + '...'
        
        if 'intOnlyRecipient' in fields and fields['intOnlyRecipient']:
            self.recipients = [contact.getContactFromId(db, fields['intOnlyRecipient'])]
        else:
            self.recipients = self.getRecipients(db)

    def __str__(self):
        """
            A short string representation of the Message.
            Should be called with unicode(var).
        """
        
        date = time.strftime('%Y-%m-%d %H:%M', self.sentDate)
        
        origin = u''
        if self.type == 'IM':
            for recipient in self.recipients:
                origin += unicode(recipient) + u', '
            
            origin = origin[:-2]
        elif self.sender.isMe and len(self.recipients) == 1:
            origin = u'to ' + unicode(self.recipients[0])
        elif self.sender.isMe and len(self.recipients) > 1:
            origin = u'to ' + unicode(self.recipients[0]) + u'...'
        else:
            origin = u'from ' + unicode(self.sender)
        
        return u'%s, %s: %s' % (date, origin, self.summary)
    
    def getRecipients(self, db):
        
        sql = """
            SELECT intContactId
            FROM mRecipient
            WHERE intMessageId = ?"""
        
        recipients = db.executeMany(sql, self.id)
        return [contact.getContactFromId(db, row['intContactId']) for row in recipients]

def getMessages(db):
    """
        Returns a list of the given number of messages
        that belong to the user.
    """
    
    sql = """
        SELECT
            m.intId AS intMessageId,
            m.strSummary, m.datHappened,
            ac.strType AS strMessageType,
            m.intSenderId,
            r.intOnlyRecipient
        FROM aAccount ac
            INNER JOIN mMessage m ON m.intAccountId = ac.intId
            LEFT JOIN (
                SELECT intMessageId, MIN(intContactId) AS intOnlyRecipient
                FROM mRecipient
                GROUP BY intMessageId
                HAVING COUNT(*) =1
            ) r ON r.intMessageId = m.intId
        ORDER BY m.datHappened DESC"""
    
    return [Message(db, msg) for msg in db.executeMany(sql)]
    
    

def getAllRemoteIds(db, type, accountId=None):
    """
        Returns a list of all the remote IDs for an account.
        This is useful for determining which messages on the server are new.
    """
    if type == 'imap':
        sql = """
            SELECT e.intRemoteId
            FROM mMessage m
                INNER JOIN mEmail e ON e.intMessageId = m.intId
            WHERE m.intAccountId = ?"""
    elif type == 'iPhone SMS':
        sql = """
            SELECT s.intRemoteId
            FROM mMessage m
                INNER JOIN mSms s ON s.intMessageId = m.intId
            WHERE m.intAccountId = ?"""
    elif type == 'IM':
        sql = """
            SELECT c.strRemoteId
            FROM mMessage m
                INNER JOIN mIMConversation c ON c.intMessageId = m.intId
                INNER JOIN aAccount a ON a.intId = m.intAccountId
            WHERE a.strType = 'IM'"""
    
    return db.executeMany(sql, accountId)  

def store(db, accountId, date, senderId, summary, recipientIds, messageType):
    """
        Stores a message, and return its ID.
    """    
    
    sql = """
        INSERT INTO mMessage (intAccountId, datHappened, intSenderId, strSummary)
        VALUES (?, ?, ?, ?)"""
    
    messageId = db.executeNoneReturnId(sql, (accountId, date, senderId, summary))    
    
    for recipientId in recipientIds:
        if recipientId:
            sql = """
                INSERT OR IGNORE INTO mRecipient (intMessageId, intContactId)
                VALUES (?, ?)"""
            
            db.executeNone(sql, (messageId, recipientId))
    
    return messageId

def addRecipient(db, messageId, recipientId):
    
    sql = """
        INSERT OR IGNORE INTO mRecipient (intMessageId, intContactId)
        VALUES (?, ?)"""
    
    db.executeNone(sql, (messageId, recipientId))
