import database

class Contact:
    
    def __init__(self, fields):
        self.id = fields['intContactId']
        self.forename = fields['strContactForename']
        self.surname = fields['strContactForename']
        
        if 'strContactBestAddress' in fields:
            self.bestAddress = fields['strContactBestAddress']
        if 'strContactBestAlias' in fields:
            self.bestAlias = fields['strContactBestAlias']
    
    def __str__(self):            
        
        if self.forename and self.surname:
            return self.forename + ' ' + self.surname
        
        elif self.surname:
            return '? ' + self.surname
            
        elif self.forename:
            return self.forename + ' ?'
            
        elif self.bestAlias:
            return self.bestAlias
                    
        elif self.bestAddress:
            return self.bestAddress
            
        else:
            return '?'

def addContact(user, addressType, address, alias=None):
    
    if not address:
        print 'Address is empty'
        return None
    
    address = address.lower()
    
    sql = """
        SELECT c.intId AS intContactId
        FROM cContact c
            INNER JOIN cAddress a ON c.intId = a.intContactId
        WHERE c.strUser = %s
            AND a.enmAddressType = %s
            AND a.strAddress = %s"""
    
    result = database.executeOneToDictionary(sql, (user, addressType, address))
    
    if result == None:
        
        sql = """
            INSERT INTO cContact (strUser)
            VALUES (%s)"""
        
        cursor = database.execute(sql, user)
        
        contactId = cursor.lastrowid
        cursor.close()
        
        sql = """
            INSERT INTO cAddress (intContactId, enmAddressType, strAddress, strAlias, bitBestAddress)
            VALUES (%s, %s, %s, %s, 1)"""
        
        database.execute(sql, (contactId, addressType, address, alias)).close()
    else:
        contactId = result['intContactId']
        
    return contactId
    
def getContacts(user):
    
    sql = """
        SELECT 
            c.intId AS intContactId,
            c.strForename AS strContactForename,
            c.strSurname AS strContactForename,
            a.strAddress AS strContactBestAddress,
            a.strAlias AS strContactBestAlias
        FROM cContact c
            INNER JOIN cAddress a ON c.intId = a.intContactId
        WHERE c.strUser = %s
            AND c.bitIsMe = 0
            AND a.bitBestAddress = 1"""
    
    return [Contact(contact) for contact in database.executeManyToDictionary(sql, user)]
            
def getContactFromId(id):
    
    sql = """
        SELECT 
            c.intId AS intContactId,
            c.strForename AS strContactForename,
            c.strSurname AS strContactForename
        FROM cContact c"""
    
    return Contact(database.executeOneToDictionary(sql, user))
    
    