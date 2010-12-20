import database

def addContact(user, addressType, address, alias=None):
    
    if not address:
        print 'Address is empty'
        return None
    
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
            c.strForename,
            c.strSurname,
            a.strAddress AS strBestAddress,
            a.strAlias AS strBestAlias
        FROM cContact c
            INNER JOIN cAddress a ON c.intId = a.intContactId
        WHERE c.strUser = %s
            AND c.bitIsMe = 0
            AND a.bitBestAddress = 1"""
    
    return database.executeManyToDictionary(sql, user)
    
def getName(contact):
    
    if contact['strForename'] and contact['strSurname']:
        return contact['strForename'] + ' ' + contact['strSurname']
    
    elif contact['strSurname']:
        return '? ' + contact['strSurname']
        
    elif contact['strForename']:
        return contact['strForename'] + ' ?'
    
    elif contact['strBestAlias'] and contact['strBestAddress']:
        return ' (' + contact['strBestAlias'] + ', ' + contact['strBestAddress'] + ')'
        
    elif contact['strBestAlias']:
        return ' (' + contact['strBestAlias'] + ')'
        
    elif contact['strBestAddress']:
        return ' (' + contact['strBestAddress'] + ')'
        
    else:
        return '?'
        
def getShortName(contact):
    
    if contact['strForename'] and contact['strSurname']:
        return contact['strForename'] + ' ' + contact['strSurname']
    
    elif contact['strSurname']:
        return '? ' + contact['strSurname']
        
    elif contact['strForename']:
        return contact['strForename'] + ' ?'
        
    elif contact['strBestAlias']:
        return contact['strBestAlias']
                
    elif contact['strBestAddress']:
        return contact['strBestAddress']
        
    else:
        return '?'
        