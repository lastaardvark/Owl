# coding=utf8

import os, sys
from datetime import datetime
import elementtree.ElementTree as etree

sys.path.append(os.path.join(os.getcwd()))

import contact, message

class ChatLogGetter:
    
    def __init__(self, db, encryptionKey = None):
        """
            Creates a new IPhoneGetter, with a user and a dictionary of account details.
            If an encryption key is given, it uses this to encrypt the text messages.
        """
        self.db = db
        self.encryptionKey = encryptionKey
        self.needToStop = False
        
        self.path = '/Volumes/Maxtor2/Before/Communication/Instant Messaging/2010/friends and family/ben.heley@gmail.com/'
    
    def getNewMessageIds(self):        
        return self.parseDirectory(self.path)
    
    
    def parseDirectory(self, directory, idsSoFar=[]):
        
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            if os.path.isdir(path):
                idsSoFar = self.parseDirectory(path, idsSoFar)
            elif item == '.DS_Store':
                pass
            elif self.getFileType(path):
                idsSoFar.append(path.replace(self.path, ''))
        
        return idsSoFar
                

    def getFileType(self, filePath):
        
        file = open(filePath, 'r')
        line1 = file.readline()
        line2 = file.readline()
        file.close()
        if line2.startswith('<chat xmlns="http://purl.org/net/ulf/ns/0.'):
            return 'Adium'
        
        return None
    
    def createAccount(self, service, username):
        print ''
        print 'Account:'
        print u'Service: ' + service
        print u'Username: ' + username
    
    def createContact(self, email, alias):
        print ''
        print 'Contact:'
        print u'Email: ' + email
        print u'Alias: ' + alias
    
    def processLog(self, id):
        path = os.path.join(self.path, id)
        if self.getFileType(path) == 'Adium':
            
            self.processAdiumLog(path)
    
    def processAdiumLog(self, path):
        xml = etree.parse(path)
        root = xml.getroot()
        
        username = ''
        service = ''
        for name, value in root.items():            
            if name == 'account':
                username = value
            if name == 'service':
                service = value
        
        self.createAccount(username, service)
        
        for child in root.getchildren():
            if child.tag.endswith('message'):
                self.createContact(child.attrib['sender'], child.attrib['alias'])
                wrapper = child.getchildren()[0]
                node = wrapper.getchildren()[0]
                print child.attrib['time']
                print node.text
                print ''
        
c = ChatLogGetter(None)

ids = c.getNewMessageIds()

id = ids[13]

c.processLog(id)