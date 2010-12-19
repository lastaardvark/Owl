import database

def addContact(user, addressType, address, alias=None):
    
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
            INSERT INTO cAddress (intContactId, enmAddressType, strAddress, strAlias)
            VALUES (%s, %s, %s, %s)"""
        
        database.execute(sql, (contactId, addressType, address, alias)).close()
    else:
        contactId = result['intContactId']
        
    return contactId