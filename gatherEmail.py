from imapEmail import imapEmail
import email, HTMLParser, re
import contact, database, encryption, settings

class HtmlStripper(HTMLParser.HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def _stripTags(html):
    s = HtmlStripper()
    try:
        s.feed(html)
        return s.get_data()
    except HTMLParser.HTMLParseError:
        return re.sub("<\/?[^>]*>", "", html)

def getEmail(user, accountId, emailAddress, username, password, server='imap.gmail.com', port=993, encryptUsing=None):
    
    sql = "DELETE FROM mRecipient"   
    database.execute(sql).close()
    
    sql = "DELETE FROM cAddress"   
    database.execute(sql).close()
    
    sql = "DELETE FROM mEmail"   
    database.execute(sql).close()
        
    sql = "DELETE FROM mMessage"   
    database.execute(sql).close()
    
    sql = "DELETE FROM cContact"   
    database.execute(sql).close()
    
    server = imapEmail(emailAddress, server, port)
    server.login(username, password)
    ids = server.getMailIds()[:10]
    
    for id in ids:

        print id

        email = server.getMailFromId(id)
        
        strippedBody = _stripTags(email['body'])
        body = email['body']
        
        if encryptUsing:
            body = encryption.encrypt(encryptUsing, body)
            strippedBody = encryption.encrypt(encryptUsing, strippedBody)
        
        addEmailToDatabase(user, emailAddress, accountId, id, email['date'], email['subject'], email['from'], email['to'], body, strippedBody)

    server.logout()

def addEmailToDatabase(user, emailAddress, accountId, remoteId, date, subject, sender, to, body, bodyNoHtml):
    
    alias, address = email.Utils.parseaddr(sender)
    sender = contact.addContact(user, 'email', address, alias)
    
    sql = """
        INSERT INTO mMessage (intAccountId, datHappened, intSenderId)
        VALUES (%s, %s, %s)"""
    
    cursor = database.execute(sql, (accountId, date, sender))
    
    messageId = cursor.lastrowid
    cursor.close()
        
    sql = """
        INSERT INTO mEmail (intMessageId, strRemoteId, strSubject, strBody, strBodyNoHtml)
        VALUES (%s, %s, %s, %s, %s)"""
    
    database.execute(sql, (messageId, remoteId, subject, body, bodyNoHtml))
    
    for alias, address in email.Utils.getaddresses(to):
        recipient = contact.addContact(user, 'email', address, alias)
        
        sql = """
            REPLACE INTO mRecipient (intMessageId, intContactId)
            VALUES (%s, %s)"""
        
        database.execute(sql, (messageId, recipient)).close()
    