# coding=utf8

from imapEmail import ImapEmail
import emailMessage
import email, HTMLParser, os, re, sys

sys.path.append(os.path.join(os.getcwd()))

import contact, database, encryption, message, settings, stringFunctions


class ImapGetter:
    
    def __init__(self, account, encryptionKey = None):
        """
            Creates a new ImapGetter, with a user and a dictionary of account details.
            If an encryption key is given, it uses this to encrypt the bodies of emails.
        """
        self.account = account
        self.encryptionKey = encryptionKey
        self.needToStop = False
    
    def _connect(self):
        """
            Connect and log-into the IMAP server.
        """
        
        server = ImapEmail(self.account.userAddress, self.account.server, self.account.port)
        server.login(self.account.username, self.account.password)
        return server
        
    def getNewMessageIds(self, db):
        """
            Returns the remote IDs of any new messages on the server.
        """
        
        server = self._connect()
        serverIds = [msgId for msgId in server.getMailIds()]
        server.logout()
        
        storedIds = [int(msg['intRemoteId']) for msg in message.getAllRemoteIds(db, 'imap', self.account.id)]

        self.idsToFetch = [msg for msg in serverIds if storedIds.count(msg) == 0]

        
    def downloadNewMessages(self, db, progressBroadcaster = None):
        """
            Download any new messages from the server.
            If a progressBroadcaster function is specified, it will be called after each
            message is stored.
        """
        
        self.idsToFetch.sort(reverse=True) # Do oldest first.
        
        server = self._connect()
                
        while len(self.idsToFetch) > 0:
        
            if self.needToStop:
                break
            
            id = self.idsToFetch.pop()
            
            self._downloadEmail(db, id, server)
            
            if progressBroadcaster and not self.needToStop:
                progressBroadcaster(len(self.idsToFetch))
                
        server.logout()
    

    def _downloadEmail(self, db, id, server):
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
        senderId = contact.addEmptyContact(db, 'email', address, alias)
        
        recipientIds = [contact.addEmptyContact(db, 'email', address, alias) for alias, address in email['to']]
        
        messageId = message.store(db, self.account.id, email['date'], senderId, email['subject'], recipientIds, 'imap')
        
        emailMessage.store(db, messageId, id, email['subject'], bodyPlain, bodyHtml, raw)
    
    def stop(self):
        """
            Stops us fetching any more messages once the current message has finished.
        """
        
        self.needToStop = True
        