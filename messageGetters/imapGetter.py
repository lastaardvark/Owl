from imapEmail import imapEmail
import email, HTMLParser, os, re, sys

sys.path.append(os.path.join(os.getcwd()))

import contact, database, encryption, message, settings, stringFunctions

def reset():
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
    
    sql = "INSERT INTO cContact (strUser, bitIsMe, strForename, strSurname) VALUES ('paul', 1, 'Paul', 'Roberts')"
    cursor = database.execute(sql)
    ourContactId = cursor.lastrowid
    cursor.close()
    
    sql = "INSERT INTO cAddress(intContactId, enmAddressType, strAddress, bitBestAddress, strAlias) VALUES (%s, 'email', 'proberts84@gmail.com', 1, 'Paul Roberts')"
    database.execute(sql, ourContactId).close()

class ImapGetter:
    
    def __init__(self, username, account, encryptionKey = None):
        self.username = username
        self.account = account
        self.encryptionKey = encryptionKey
        self.needToStop = False
        
        #reset()
    
    def _connect(self):
        server = imapEmail(self.account['strEmailAddress'], self.account['strServer'], self.account['intPort'])
        server.login(self.account['strUsername'], self.account['strPassword'])
        return server
        
    def getNewMessageIds(self):
        server = self._connect()
        serverIds = [str(msgId) for msgId in server.getMailIds()]
        server.logout()
        
        storedIds = [msg['strRemoteId'] for msg in message.getAllRemoteIds(self.account['intAccountId'])]
        
        return [msg for msg in serverIds if storedIds.count(msg) == 0]
        
    def downloadNewMessages(self, ids = None, progressBroadcaster = None):
        if not ids:
            ids = self.getNewMessageIds()
        
        server = self._connect()
        
        done = 0
        for id in ids:
        
            if self.needToStop:
                break
            
            self._downloadEmail(id, server)
            
            done += 1            
            if progressBroadcaster and not self.needToStop:
                progressBroadcaster(done)
                
        server.logout()
    

    def _downloadEmail(self, id, server):
        email = server.getMailFromId(id)
        
        body = email['body']
        raw = email['raw']
            
        if self.encryptionKey:
            body = encryption.encrypt(self.encryptionKey, body)
            raw = encryption.encrypt(self.encryptionKey, raw)
                        
        alias, address = email['from']
        senderId = contact.addContact(self.username, 'email', address, alias)
        
        recipientIds = [contact.addContact(self.username, 'email', address, alias) for alias, address in email['to']]
        
        messageId = message.store(self.account['intAccountId'], email['date'], senderId, email['subject'], recipientIds)
        
        sql = """
            INSERT INTO mEmail (intMessageId, strRemoteId, strSubject, strBody, strRaw)
            VALUES (%s, %s, %s, %s, %s)"""
        
        database.execute(sql, (messageId, id, email['subject'], body, raw)).close()
    
    def stop(self):
        self.needToStop = True
        
if __name__ == '__main__':
    
    imapGetter = ImapGetter( \
        'tla', {'strEmailAddress': 'tla.owl.test@gmail.com', 
                'strServer': 'imap.gmail.com',
                'intPort': 993, 
                'strUsername': 'tla.owl.test', 
                'strPassword': settings.settings['testPassword'],
                'intAccountId': 4
                })
                
    #ids = imapGetter.getNewMessageIds()
    
    #print type(ids[0])
    #print ids
    server = imapGetter._connect()
    
    email = server.getMailFromId(4)
  #  print email
                
                
                
                
    
    