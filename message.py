# coding=utf8

import contact, database

_messages = {}
_user = ''
_password = ''

class Message:
    
    def __init__(self, fields):
        """
            Initializes a new Message using a dictionary
            of database fields.
        """
        
        self.id = fields['intMessageId']
        
        if self.id in _messages:
            
            self.__dict__ = _messages[self.id].__dict__
        
        else:
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

def initialize(user, password):
    global _user
    global _password
    _user = user
    _password = password

def getMessages():
    return _messages.values()

def refresh():
    """
        Returns a list of the given number of messages
        that belong to the user.
    """
    
    sql = """
        SELECT
            m.intId AS intMessageId,
            m.strSummary, m.datHappened,
            ac.enmType AS strMessageType,
            m.intSenderId
        FROM aAccount ac
            INNER JOIN mMessage m ON m.intAccountId = ac.intId
        WHERE ac.strUser = %s
        ORDER BY m.datHappened DESC"""
    
    messages = [Message(msg) for msg in database.executeManyToDictionary(sql, _user)]
    
    global _messages
    _messages = dict([[message.id, message] for message in messages])
    

def getAllRemoteIds(accountId, type):
    """
        Returns a list of all the remote IDs for an account.
        This is useful for determining which messages on the server are new.
    """
    if type == 'imap':
        sql = """
            SELECT e.intRemoteId
            FROM mMessage m
                INNER JOIN mEmail e ON e.intMessageId = m.intId
            WHERE m.intAccountId = %s"""
    elif type == 'iPhone SMS':
        sql = """
            SELECT s.intRemoteId
            FROM mMessage m
                INNER JOIN mSms s ON s.intMessageId = m.intId
            WHERE m.intAccountId = %s"""
    
    return database.executeManyToDictionary(sql, accountId)  

def store(accountId, date, senderId, summary, recipientIds, messageType):
    """
        Stores a message, and return its ID.
    """    
    
    sql = """
        INSERT INTO mMessage (intAccountId, datHappened, intSenderId, strSummary)
        VALUES (%s, %s, %s, %s)"""
    
    cursor = database.execute(sql, (accountId, date, senderId, summary))    
    messageId = cursor.lastrowid
    cursor.close()
    
    for recipientId in recipientIds:
        if recipientId:
            sql = """
                REPLACE INTO mRecipient (intMessageId, intContactId)
                VALUES (%s, %s)"""
            
            database.execute(sql, (messageId, recipientId)).close()

    _messages[messageId] = Message({
        'intMessageId': messageId, 
        'datHappened': date, 
        'intSenderId': senderId, 
        'strSummary': summary,
        'strMessageType': messageType})
    
    return messageId
