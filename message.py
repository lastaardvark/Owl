# coding=utf8

import contact

class Message:
    
    def __init__(self, fields):
        """
            Initializes a new Message using a dictionary
            of database fields.
        """
        
        self.id = fields['intMessageId']
        
        self.sender = contact.getContactFromId(fields['intSenderId'])
        
        self.sentDate = fields['datHappened']
        self.summary = fields['strSummary'].replace(u'\n', u'')
        if fields['strMessageType'] == 'imap':
            self.type = 'email'
        elif fields['strMessageType'] == 'iPhone SMS':
            self.type = 'SMS'
        
        if len(self.summary) > 77:
            self.summary = self.summary[:77] + '...'

    def __str__(self):
        """
            A short string representation of the Message.
            Should be called with unicode(var).
        """
        
        date = self.sentDate.strftime('%Y-%m-%d %H:%M')

        return u'%s, %s: %s' % (date, unicode(self.sender), self.summary)


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
            m.intSenderId
        FROM aAccount ac
            INNER JOIN mMessage m ON m.intAccountId = ac.intId
        ORDER BY m.datHappened DESC"""
    
    return [Message(msg) for msg in db.owlExecuteMany(sql)]
    
    

def getAllRemoteIds(db, accountId, type):
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
    
    return db.owlExecuteMany(sql, accountId)  

def store(db, accountId, date, senderId, summary, recipientIds, messageType):
    """
        Stores a message, and return its ID.
    """    
    
    sql = """
        INSERT INTO mMessage (intAccountId, datHappened, intSenderId, strSummary)
        VALUES (?, ?, ?, ?)"""
    
    messageId = sqlite.owlExecuteNoneReturnId(sql, (accountId, date, senderId, summary))    
    
    for recipientId in recipientIds:
        if recipientId:
            sql = """
                REPLACE INTO mRecipient (intMessageId, intContactId)
                VALUES (%s, %s)"""
            
            db.owlExecuteNone(sql, (messageId, recipientId))
    
    return messageId
