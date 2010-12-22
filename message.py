import contact, database

def getMessages(user, number=50):
    
    sql = """
        SELECT
            m.intId AS intMessageId,
            m.strSummary, m.datHappened,
            e.strRemoteId,
            c.intId AS intContactId,
            c.strForename,
            c.strSurname,
            a.strAddress AS strBestAddress,
            a.strAlias AS strBestAlias
        FROM mAccount ac
            INNER JOIN mMessage m ON m.intAccountId = ac.intId
            INNER JOIN cContact c ON c.intId = m.intSenderId
            INNER JOIN cAddress a ON c.intId = a.intContactId
            LEFT JOIN mEmail e ON e.intMessageId = m.intId
        WHERE ac.strUser = %s
            AND a.bitBestAddress = 1
        ORDER BY m.datHappened DESC
        LIMIT %s"""
        
    return database.executeManyToDictionary(sql, (user, number))

def getAllRemoteIds(accountId):
    sql = """
        SELECT e.strRemoteId
        FROM mMessage m
            INNER JOIN mEmail e ON e.intMessageId = m.intId
        WHERE m.intAccountId = %s"""
    
    return database.executeManyToDictionary(sql, accountId)  
    
def getName(message):
    summary = message['strSummary'].replace(u'\n', u'')
    
    if len(summary) > 77:
        summary = summary[:77] + '...'
        
    date = message['datHappened'].strftime('%Y-%m-%d %H:%M')
    remoteId = message['strRemoteId']
    if not remoteId:
        remoteId = ''
    return date + ', ' + contact.getShortName(message) + ': ' + summary + ' (' + remoteId + ')'

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
