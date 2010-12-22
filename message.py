import database
from contact import Contact

class Message:
    
    def __init__(self, fields):
        self.id = fields['intMessageId']
        self.sender = Contact(fields)
        self.sentDate = fields['datHappened']
        self.summary = fields['strSummary'].replace(u'\n', u'')
        
        if len(self.summary) > 77:
            self.summary = self.summary[:77] + '...'

    def __str__(self):
        date = self.sentDate.strftime('%Y-%m-%d %H:%M')

        return u'%s, %s: %s' % (date, unicode(self.sender), self.summary)

def getMessages(user, number=50):
    
    sql = """
        SELECT
            m.intId AS intMessageId,
            m.strSummary, m.datHappened,
            e.strRemoteId,
            c.intId AS intContactId,
            c.strForename AS strContactForename,
            c.strSurname AS strContactSurname,
            a.strAddress AS strContactBestAddress,
            a.strAlias AS strContactBestAlias
        FROM mAccount ac
            INNER JOIN mMessage m ON m.intAccountId = ac.intId
            INNER JOIN cContact c ON c.intId = m.intSenderId
            INNER JOIN cAddress a ON c.intId = a.intContactId
            LEFT JOIN mEmail e ON e.intMessageId = m.intId
        WHERE ac.strUser = %s
            AND a.bitBestAddress = 1
        ORDER BY m.datHappened DESC
        LIMIT %s"""
        
    return [Message(msg) for msg in database.executeManyToDictionary(sql, (user, number))]

def getAllRemoteIds(accountId):
    sql = """
        SELECT e.strRemoteId
        FROM mMessage m
            INNER JOIN mEmail e ON e.intMessageId = m.intId
        WHERE m.intAccountId = %s"""
    
    return database.executeManyToDictionary(sql, accountId)  

def store(accountId, date, senderId, summary, recipientIds):

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
    
    return messageId
