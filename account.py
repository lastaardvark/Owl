# coding=utf8

import encryption, sqlite

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
    
def getAllAccounts(db):
    
    return getImapAccounts(db) + getSmsAccounts(db)