# coding=utf8

import os, sys
from datetime import datetime
import time
import elementtree.ElementTree as etree

sys.path.append(os.path.join(os.getcwd()))

import account, contact, imConversation, message, settings

class IMGetter:
    
    def __init__(self, db, encryptionKey = None):
        """
            Creates a new IPhoneGetter, with a user and a dictionary of account details.
            If an encryption key is given, it uses this to encrypt the text messages.
        """
        self.db = db
        self.encryptionKey = encryptionKey
        self.needToStop = False
        
    
    def getNewMessageIds(self, db):
        availableIds = []
        
        for path in settings.knownIMLogPaths:
            availableIds += self.parseDirectory(path, path, [])
        storedIds = message.getAllRemoteIds(db, 'IM')
        
        self.idsToFetch = [path for path in availableIds if storedIds.count(path[1]) == 0]
    
    def parseDirectory(self, root, currentDirectory, idsSoFar=[]):
        
        for item in os.listdir(currentDirectory):
            path = os.path.join(currentDirectory, item)
            if os.path.isdir(path):
                idsSoFar = self.parseDirectory(root, path, idsSoFar)
            elif item == '.DS_Store':
                pass
            elif self.getFileType(path):
                idsSoFar.append((root, path.replace(root, '')))
        
        return idsSoFar
                

    def getFileType(self, filePath):
        
        file = open(filePath, 'r')
        line1 = file.readline()
        line2 = file.readline()
        file.close()
        if line2.startswith('<chat xmlns="http://purl.org/net/ulf/ns/0.'):
            return 'Adium'
        
        return None
        
    def stop(self):
        self.needToStop = True
        
    def downloadNewConversations(self, db, progressBroadcaster = None):
        
        self.idsToFetch.sort(reverse=True) # Bias towards doing oldest first.
        
        while len(self.idsToFetch) > 0:
        
            if self.needToStop:
                break
            
            path, id = self.idsToFetch.pop()
            
            self._processLog(db, path, id)
            
            if progressBroadcaster and not self.needToStop:
                progressBroadcaster(len(self.idsToFetch))
    
    def _processLog(self, db, root, id):
        path = os.path.join(root, id)
        if self.getFileType(path) == 'Adium':            
            self._processAdiumLog(db, path, id)
    
    def _processAdiumLog(self, db, path, id):
        
        xml = etree.parse(path)
        root = xml.getroot()
        
        username = ''
        service = ''
        for name, value in root.items():            
            if name == 'account':
                username = value
            if name == 'service':
                service = value
        
        accountId, ourContactId = account.createIMAccount(db, service, username)
        
        storedConversation = False
        storedContacts = {}
        
        for child in root.getchildren():
            if child.tag.endswith('message'):
            
                alias = None
                if 'alias' in child.attrib:
                    alias = child.attrib['alias']
                address = child.attrib['sender']
                
                if address not in storedContacts:
                    contactId = contact.addEmptyContact(db, 'IM', address, alias)
                    if address.find('@') > 0:   # Crude test for email
                        contactId = contact.addAddressToExistingContact(db, contactId, 'email', address, alias)
                    
                    storedContacts[address] = contactId
                else:
                    contactId = storedContacts[address]
                
                sentTime = datetime(*time.strptime(child.attrib['time'][:19], '%Y-%m-%dT%H:%M:%S')[0:6])
                
                wrapper = child.getchildren()[0]
                node = wrapper.getchildren()[0]
                text = node.text
                
                if text:
                    if not storedConversation:
                        messageId = message.store(db, accountId, sentTime, ourContactId, text + u'...', [ourContactId], 'IM')
                        imConversation.store(db, messageId, id)
                        storedConversation = True
                    
                    if contactId != ourContactId:
                        message.addRecipient(db, messageId, contactId)
                    
                    imConversation.addEntry(db, messageId, sentTime, contactId, text)
