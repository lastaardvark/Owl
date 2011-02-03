# coding=utf8

import encryption, contact, sqlite

class Account:
    
    def __init__(self, fields):
        
        self.id = fields['intAccountId']
        self.type = fields['strType']
        self.userAddress = fields['strUserAddress']



class ImapAccount(Account):
    
    def __init__(self, fields, decryptionKey):
        
        Account.__init__(self, fields)
        
        self.server = fields['strServer']
        self.port = fields['intPort']
        self.username = fields['strUsername']
        self.password = encryption.decrypt(decryptionKey, str(fields['strPassword']))
        
class SmsAccount(Account):
    
    def __init__(self, fields):
        
        Account.__init__(self, fields)
        
        self.defaultCountry = fields['strDefaultCountry']
        
class IMAccount(Account):
    
    def __init__(self, fields):
        
        Account.__init__(self, fields)
        
        self.service = fields['strService']
        self.username = fields['strUsername']

def getImapAccounts(db, decryptionKey):

    sql = """
        SELECT 
            e.intAccountId, 
            a.strType, a.strUserAddress,
            e.strServer, e.intPort, 
            e.strUsername, e.strPassword
        FROM aAccount a
            INNER JOIN aEmailAccount e ON e.intAccountId = a.intId
        WHERE a.strType = 'imap'"""
    
    accounts = db.executeMany(sql)
    
    if not accounts:
        return None
    
    return [ImapAccount(account, decryptionKey) for account in accounts]
    
def getSmsAccounts(db):

    sql = """
        SELECT 
            s.intAccountId, 
            a.strType, a.strUserAddress,
            s.strDefaultCountry
        FROM aAccount a
            INNER JOIN aSmsAccount s ON s.intAccountId = a.intId
        WHERE strType = 'iPhone SMS'"""
    
    accounts = db.executeMany(sql)
    
    if not accounts:
        return None
    
    return [SmsAccount(account) for account in accounts]

def getIMAccounts(db):

    sql = """
        SELECT 
            s.intAccountId, 
            a.strType, a.strUserAddress,
            s.strService, s.strUsername
        FROM aAccount a
            INNER JOIN aIMAccount i ON i.intAccountId = a.intId
        WHERE a.strType = 'IM'"""
    
    accounts = db.executeMany(sql)
    
    if not accounts:
        return None
    
    return [IMAccount(account) for account in accounts]    

def getAllAccounts(db):
    
    return getImapAccounts(db) + getSmsAccounts(db)


def createAccount(db, type, userAddress):
    
    sql = """
        SELECT intId
        FROM aAccount
        WHERE strType = ?
            AND strUserAddress = ?"""
    
    result = db.executeOne(sql, (type, userAddress))
    
    if result:
        return result['intId']
    
    else:
        
        sql = """
            INSERT INTO aAccount (strType, strUserAddress)
            VALUES (?, ?)"""
        
        return db.executeNoneReturnId(sql, (type, userAddress))
    
def createIMAccount(db, service, username):
    
    if service == 'GTalk':
        username = username.replace('@googlemail.com', '@gmail.com')
        
        if username.find('@') == -1:
            username = username + '@gmail.com'
    
    ourContactId = contact.addAddressToMe(db, 'IM', username)
    
    sql = """
        SELECT intAccountId
        FROM aIMAccount
        WHERE strService = ?
            AND strUsername = ?"""
    
    result = db.executeOne(sql, (service, username))
    
    if result:
        return result['intAccountId'], ourContactId
        
    else:
        accountId = createAccount(db, 'IM', username)
        
        # We need the OR IGNORE as createAccount() could return an existing account ID.
        
        sql = """
            INSERT OR IGNORE INTO aIMAccount (intAccountId, strService, strUsername)
            VALUES (?, ?, ?)"""
        
        db.executeNone(sql, (accountId, service, username))
        
        return accountId, ourContactId
    
    
        
        