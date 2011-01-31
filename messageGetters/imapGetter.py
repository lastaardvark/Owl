# coding=utf8

from imapEmail import ImapEmail
import emailMessage
import email, HTMLParser, os, re, sys

sys.path.append(os.path.join(os.getcwd()))

import contact, database, encryption, message, settings, stringFunctions


class ImapGetter:
    
    def __init__(self, db, account, encryptionKey = None):
        """
            Creates a new ImapGetter, with a user and a dictionary of account details.
            If an encryption key is given, it uses this to encrypt the bodies of emails.
        """
        self.account = account
        self.encryptionKey = encryptionKey
        self.needToStop = False
        self.db = db
    
    def _connect(self):
        """
            Connect and log-into the IMAP server.
        """
        
        server = ImapEmail(self.account['strUserAddress'], self.account['strServer'], self.account['intPort'])
        server.login(self.account['strUsername'], self.account['strPassword'])
        return server
        
    def getNewMessageIds(self):
        """
            Returns the remote IDs of any new messages on the server.
        """
        
        server = self._connect()
        serverIds = [msgId for msgId in server.getMailIds()]
        server.logout()
        
        storedIds = [int(msg['intRemoteId']) for msg in message.getAllRemoteIds(self.db, self.account['intAccountId'], 'imap')]

        return [msg for msg in serverIds if storedIds.count(msg) == 0]
        
    def downloadNewMessages(self, ids = None, progressBroadcaster = None):
        """
            Download any new messages from the server.
            If the remote IDs are already known, they can be passed in as ids.
            If a progressBroadcaster function is specified, it will be called after each
            message is stored.
        """
        
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
        """
            Downloads the email with the given remote ID and stores
            it in the database.
        """
        
        email = server.getMailFromId(id)
        
        bodyPlain = email['bodyPlainText']
        bodyHtml = email['bodyHtml']
        raw = email['raw']
            
        if self.encryptionKey:
            bodyPlain = encryption.encrypt(self.encryptionKey, bodyPlain)
            bodyHtml = encryption.encrypt(self.encryptionKey, bodyHtml)
            raw = encryption.encrypt(self.encryptionKey, raw)
                        
        alias, address = email['from']
        senderId = contact.addEmptyContact(self.db, 'email', address, alias)
        
        recipientIds = [contact.addEmptyContact(self.db, 'email', address, alias) for alias, address in email['to']]
        
        messageId = message.store(self.db, self.account['intAccountId'], email['date'], senderId, email['subject'], recipientIds, 'imap')
        
        emailMessage.store(self.db, messageId, id, email['subject'], bodyPlain, bodyHtml, raw)
    
    def stop(self):
        """
            Stops us fetching any more messages once the current message has finished.
        """
        
        self.needToStop = True
        