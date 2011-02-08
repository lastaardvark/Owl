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
        
        storedIds = [unicode(id['strRemoteId']) for id in storedIds]
        
        self.idsToFetch = [path for path in availableIds if storedIds.count(unicode(path[1])) == 0]
    
    def parseDirectory(self, root, currentDirectory, idsSoFar=[]):
        
        for item in os.listdir(currentDirectory):
            path = os.path.join(currentDirectory, item)
            if os.path.isdir(path):
                idsSoFar = self.parseDirectory(root, path, idsSoFar)
            elif item == '.DS_Store':
                pass
            elif item.endswith('_temp'):
                pass
            elif self.getFileType(path):
                idsSoFar.append((root, path.replace(root, '')))
        
        return idsSoFar
                

    def getFileType(self, filePath):
        
        file = open(filePath, 'r')
        line1 = file.readline()
        line2 = file.readline()
        file.close()
        if line2 and line2.startswith('<chat xmlns="http://purl.org/net/ulf/ns/0.'):
            return 'Adium'
        elif line1.startswith('<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head><body style=') \
            and filePath.find('Messenger ') != -1:
            return 'MSN'
        #else:
        #    print ''
        #    print 'Unknown type:'
        #    print filePath
            
        return None
        
    def stop(self):
        self.needToStop = True
        
    def downloadNewConversations(self, db, questionAsker, progressBroadcaster = None):
        
        self.questionAsker = questionAsker
        
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
        if self.getFileType(path) == 'MSN':            
            self._processMsnLog(db, path, id)
    
    def _processAdiumLog(self, db, path, id):
        
        file = open(path, 'r')
        line = file.read()
        file.close()
        
        # Line breaks confuse things later on.
        line = line.replace('<br />', '&lt;br /&gt;')
        
        writeFile = open(path + '_temp', 'w')
        writeFile.write(line)
        writeFile.close()
        
        xml = etree.parse(path + '_temp')
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
                
                if node.text:
                    text = node.text.replace('&lt;br /&gt;', '\n')
    
                    if not storedConversation:
                        messageId = message.store(db, accountId, sentTime, ourContactId, text + u'...', [ourContactId], 'IM')
                        imConversation.store(db, messageId, id)
                        storedConversation = True
                    
                    if contactId != ourContactId:
                        message.addRecipient(db, messageId, contactId)
                    
                    imConversation.addEntry(db, messageId, sentTime, contactId, text)
        
        os.remove(path + '_temp')

    def _processMsnLog(self, db, path, id):
        
        file = open(path, 'r')
        line = file.read()
        
        print id
        # Make valid XML
        line = line.replace('<meta http-equiv="Content-Type" content="text/html; charset=utf-8">', '')
        line = line.replace('<br>', '')
        line = line.replace('&nbsp;', '')
        
        writeFile = open(path + '_temp', 'w')
        writeFile.write(line)
        writeFile.close()
                
        xml = etree.parse(path + '_temp')
        root = xml.getroot()
        body = root.getchildren()[1]
        
        paragraphs = body.getchildren()
        
        firstLine = paragraphs[0].text
        to = firstLine[4:firstLine.find('Start Time')]
        start = firstLine[firstLine.find('Start Time: ') + len('Start Time: '):]
        start = start[:start.find(';')]
        
        substring = id[id.rfind('Messenger ') + len('Messenger '): ]
        date = substring[ : 10]
        
        participant = substring[1: substring.rfind('.htm')]
        
        def findAllAliases(paragraphs):
            aliases = []
            for paragraph in paragraphs:
                if paragraph.text and paragraph.text.find(' says: (') != -1:
                    alias = paragraph.text[: paragraph.text.find(' says: (')]
                    if not alias in aliases:
                        aliases.append(alias)
            return aliases
        
        aliases = findAllAliases(paragraphs)
        
        self.answer = None
        
        if len(aliases) > 2:
            question = 'An MSN log is ambiguous about which of the following aliases is you,\nand which is '
            question += to + '.\nPlease select all the aliases that are you.'
        else:
            question = 'An MSN log is ambiguous about which of the following aliases is you,\nand which is '
            question += to + '.\nPlease click on the alias that is you.'
        
        
        self.questionAsker(aliases, 'Interpreting an IM Log', question, self.receiveAnswer, len(aliases) > 2)
        
        while not self.answer and not self.needToStop:
            time.sleep(1)
        
        if type(self.answer) != type([]):
            self.answer = [self.answer]
        ourAliases = self.answer
        
        theirAlias = [alias for alias in aliases if alias not in self.answer][0]
        
        accountId, ourContactId = account.createIMAccount(db, 'MSN', 'Unknown')
        theirContactId = contact.addEmptyContact(db, 'IM', to, theirAlias)
        
        messageId = None
        
        i = 1
        while i < len(paragraphs):
            line1 = paragraphs[i].text
            if not line1 or line1.find(' says: (') == -1:
                i+= 1  # Skip over another "To... Start Time..." line if the window was shut
            else:
                alias = line1[: line1.find(' says: (')]
                timeReceived = line1[line1.rfind('(') + 1: line1.rfind(')')]
                timeReceived = datetime(*time.strptime(date + ' ' + timeReceived, '%d.%m.%Y %H:%M:%S')[0:6])
                
                i += 1
                text = paragraphs[i].text
                i += 1
                
                if text:
                    if not messageId:
                        messageId = message.store(db, accountId, timeReceived, ourContactId, text + u'...', [ourContactId, theirContactId], 'IM')
                        imConversation.store(db, messageId, id)
                    
                    if alias in ourAliases:
                        contactId = ourContactId
                    else:
                        contactId = theirContactId
                    
                    imConversation.addEntry(db, messageId, timeReceived, contactId, text)
        
        os.remove(path + '_temp')
    
    def receiveAnswer(self, answer):
        self.answer = answer