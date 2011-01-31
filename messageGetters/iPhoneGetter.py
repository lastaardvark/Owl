# coding=utf8

import os, sqlite3, sys, time
from datetime import datetime

sys.path.append(os.path.join(os.getcwd()))

import contact, message, smsMessage, sqlite

class IPhoneGetter:
    
    def __init__(self, db, account, encryptionKey = None):
        """
            Creates a new IPhoneGetter, with a user and a dictionary of account details.
            If an encryption key is given, it uses this to encrypt the text messages.
        """
        self.db = db
        self.account = account
        self.encryptionKey = encryptionKey
        self.needToStop = False
        self.getDatabaseConnections()
        self.ourId = contact.addEmptyContact(db, 'phone', account['strUserAddress'])
    
    def getDatabaseConnections(self):
    
        basePath = os.path.expanduser('~/Library/Application Support/MobileSync/Backup')
        
        for folder in os.listdir(basePath):
            path = os.path.join(basePath, folder)
            if os.path.isdir(path):
                for file in os.listdir(path):
                    filePath = os.path.join(path, file)
                    if file != '.DS_Store':
                        try:
                            con = sqlite3.connect(filePath)
                            cur = con.cursor()
                            sql = """
                                SELECT COUNT(*) FROM sqlite_master
                                WHERE type = 'table'
                                    AND name IN ('message', 'msg_group', 'group_member', 'msg_pieces')"""
                            cur.execute(sql)
                            
                            found = cur.fetchone()[0]
                            if found == 4:
                                self.smsConnection = con
                                
                            cur.close()
                            
                            cur = con.cursor()
                            sql = """
                                SELECT COUNT(*) FROM sqlite_master
                                WHERE type = 'table'
                                    AND name IN ('ABPerson', 'ABStore', 'ABMultiValue', 'ABGroup')"""
                            cur.execute(sql)
                            
                            found = cur.fetchone()[0]
                            if found == 4:
                                self.contactConnection = con
                                
                            cur.close()
                        except sqlite3.DatabaseError, error: # Not an sqlite file.
                            pass
    
    
    def getNewMessageIds(self):
        """
            Returns the remote IDs of any new messages on the server.
        """
        
        self.updateContacts()
        
        if not self.smsConnection:
            return []
        
        sql = """
            SELECT ROWID FROM message
            WHERE address IS NOT NULL
                AND text IS NOT NULL
            ORDER BY ROWID;"""
        
        remoteIds = sqlite.executeManyToDictionary(self.smsConnection, sql)
        
        remoteIds = [row['ROWID'] for row in remoteIds]
        storedIds = [int(msg['intRemoteId']) for msg in message.getAllRemoteIds(self.db, self.account['intAccountId'], 'iPhone SMS')]
        
        return [msg for msg in remoteIds if storedIds.count(msg) == 0]
    
    def updateContacts(self):
        
        if not self.contactConnection:
            return
        
        sql = """
            SELECT p.ROWID, p.First, p.Last, mv.property, mv.value
            FROM ABPerson p
                INNER JOIN ABMultiValue mv ON mv.record_id = p.ROWID
            WHERE mv.property IN (3, 4) -- Phone, Email
            ORDER BY p.ROWID"""
        
        contacts = sqlite.executeManyToDictionary(self.contactConnection, sql)
        
        addedContacts = {}
        
        for person in contacts:
            address = person['value']
            
            rowId = person['ROWID']
            if person['property'] == 3:
                addressType = 'phone'
                address = address.replace(' ', '')
                address = address.replace('(', '').replace(')', '')
                address = address.replace('-', '')
                address = self.internationalizeNumber(address, self.account['strDefaultCountry'])
            elif person['property'] == 4:
                addressType = 'email'
            
            if rowId in addedContacts:
                newId = contact.addAddressToExitingContact(self.db, addedContacts[rowId], addressType, address)
                addedContacts[rowId] = newId
            else:
                contactId = contact.createContact(self.db, person['First'], person['Last'], addressType, address)
                addedContacts[rowId] = contactId
    
    def stop(self):
        self.needToStop = True
        
    def downloadNewMessages(self, ids = None, progressBroadcaster = None):
        """
            Download any new messages from the server.
            If the remote IDs are already known, they can be passed in as ids.
            If a progressBroadcaster function is specified, it will be called after each
            message is stored.
        """
        
        if not ids:
            ids = self.getNewMessageIds()
        
        done = 0
        for id in ids:
        
            if self.needToStop:
                break
            
            time.sleep(0.0001) # Keep GUI thread running smoothly
            
            self._downloadText(id)
            
            done += 1            
            if progressBroadcaster and not self.needToStop:
                progressBroadcaster(done)
         
        self.smsConnection.close()
        self.contactConnection.close()
        
    
    def internationalizeNumber(self, number, country):
        
        if number[0] == '0':
            if country.lower() == 'uk':
                number = '+44' + number[1:]
            else:
                print 'Unknown country: ' + country
        
        return number
    
    def _downloadText(self, id):
        
        sql = """
            SELECT address, date, text, country, association_id
            FROM message
            WHERE ROWID = ?;"""

        msg = sqlite.executeOneToDictionary(self.smsConnection, sql, id)
        date = datetime.fromtimestamp(msg['date'])
        
        number = self.internationalizeNumber(msg['address'], msg['country'])
        
        numberId = contact.addEmptyContact(self.db, 'phone', number)
        
        if msg['association_id'] == 0:
            senderId = numberId
            recipientId = self.ourId
        else:
            senderId = self.ourId
            recipientId = numberId
        
        
        messageId = message.store(self.db, self.account['intAccountId'], date, senderId, msg['text'], [recipientId], 'iPhone SMS')
        
        smsMessage.store(self.db, messageId, id, msg['text'])
        
        