# coding=utf8

import os, re, sqlite3, sys, time
from datetime import datetime

sys.path.append(os.path.join(os.getcwd()))

import contact, message, smsMessage, sqlite

class IPhoneGetter:
    
    def __init__(self, db, account, encryptionKey = None):
        """
            Creates a new IPhoneGetter, with a user and a dictionary of account details.
            If an encryption key is given, it uses this to encrypt the text messages.
        """
        self.account = account
        self.encryptionKey = encryptionKey
        self.needToStop = False
        self.getDatabaseConnections()
        self.ourId = contact.addEmptyContact(db, 'phone', account.userAddress)
    
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
                                self.smsFile = filePath
                                
                            cur.close()
                            
                            cur = con.cursor()
                            sql = """
                                SELECT COUNT(*) FROM sqlite_master
                                WHERE type = 'table'
                                    AND name IN ('ABPerson', 'ABStore', 'ABMultiValue', 'ABGroup')"""
                            cur.execute(sql)
                            
                            found = cur.fetchone()[0]
                            if found == 4:
                                self.contactFile = filePath
                                
                            cur.close()
                        except sqlite3.DatabaseError, error: # Not an sqlite file.
                            pass
    
    
    def getNewMessageIds(self, db):
        """
            Returns the remote IDs of any new messages on the server.
        """
        
        self.updateContacts(db)
        
        if not self.smsFile:
            return []
        
        sql = """
            SELECT ROWID FROM message
            WHERE address IS NOT NULL
                AND text IS NOT NULL
            ORDER BY ROWID;"""
        
        connection = sqlite3.connect(self.smsFile)
        
        remoteIds = sqlite.executeManyToDictionary(connection, sql)
        
        remoteIds = [row['ROWID'] for row in remoteIds]
        storedIds = [int(msg['intRemoteId']) for msg in message.getAllRemoteIds(db, 'iPhone SMS', self.account.id)]
        
        self.idsToFetch = [msg for msg in remoteIds if storedIds.count(msg) == 0]
        
        connection.close()
    
    def updateContacts(self, db):
        
        if not self.contactFile:
            return
        
        connection = sqlite3.connect(self.contactFile)
        
        sql = """
            SELECT p.ROWID, p.First, p.Last, mv.property, mv.value
            FROM ABPerson p
                INNER JOIN ABMultiValue mv ON mv.record_id = p.ROWID
            WHERE mv.property IN (3, 4) -- Phone, Email
            ORDER BY p.ROWID"""
        
        contacts = sqlite.executeManyToDictionary(connection, sql)
        
        addedContacts = {}
        
        for person in contacts:
            address = person['value']
            
            rowId = person['ROWID']
            if person['property'] == 3:
                addressType = 'phone'
                address = address.replace(' ', '')
                address = address.replace('(', '').replace(')', '')
                address = address.replace('-', '')
                address = self.internationalizeNumber(address, self.account.defaultCountry)
            elif person['property'] == 4:
                addressType = 'email'
            
            if rowId in addedContacts:
                newId = contact.addAddressToExistingContact(db, addedContacts[rowId], addressType, address)
                addedContacts[rowId] = newId
            else:
                contactId = contact.createContact(db, person['First'], person['Last'], addressType, address)
                addedContacts[rowId] = contactId
    
        connection.close()
        
    def stop(self):
        self.needToStop = True
        
    def downloadNewMessages(self, db, progressBroadcaster = None):
        """
            Download any new messages from the server.
            If the remote IDs are already known, they can be passed in as ids.
            If a progressBroadcaster function is specified, it will be called after each
            message is stored.
        """
        
        self.idsToFetch.sort(reverse=True) # Do oldest first.
        
        connection = sqlite3.connect(self.smsFile)
        
        while len(self.idsToFetch) > 0:
            
            if self.needToStop:
                break
            
            id = self.idsToFetch.pop()
            
            time.sleep(0.0001) # Keep GUI thread running smoothly
            
            self._downloadText(db, id, connection)
            
            if progressBroadcaster and not self.needToStop:
                progressBroadcaster(len(self.idsToFetch))

        connection.close()
        
    
    def internationalizeNumber(self, number, country):
        
        if number[0] == '0':
            if country.lower() == 'uk':
                number = '+44' + number[1:]
            else:
                print 'Unknown country: ' + country
        
        return number
    
    def _downloadText(self, db, id, smsConnection):
        
        sql = """
            SELECT address, date, text, country, flags
            FROM message
            WHERE ROWID = ?;"""

        msg = sqlite.executeOneToDictionary(smsConnection, sql, id)
        date = datetime.fromtimestamp(msg['date'])
        
        number = self.internationalizeNumber(msg['address'], msg['country'])
        
        if re.match('[a-zA-Z]', number):
            # This is a bit naughty. All we have is an alias, which is not an unique identifier.
            # These are usually companies’ names, however, so duplicate aliases are unlikely.
            numberId = contact.addEmptyContact(db, 'phone', number, number, 0)
        else:
            numberId = contact.addEmptyContact(db, 'phone', number)
        
        if msg['flags'] == 2:
            senderId = numberId
            recipientId = self.ourId
        else:
            senderId = self.ourId
            recipientId = numberId
        
        
        messageId = message.store(db, self.account.id, date, senderId, msg['text'], [recipientId], 'iPhone SMS')
        
        smsMessage.store(db, messageId, id, msg['text'])
        
        