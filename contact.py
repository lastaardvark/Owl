# coding=utf8

import database

class Contact:
    
    def __init__(self, fields):
        """
            Initializes a new Contact using a dictionary
            of database fields.
        """
        
        self.id = fields['intContactId']
        self.forename = fields['strContactForename']
        self.surname = fields['strContactSurname']
        self.addresses = []
        
        if 'strContactBestAddress' in fields:
            self.bestAddress = fields['strContactBestAddress']
        if 'strContactBestAlias' in fields:
            self.bestAlias = fields['strContactBestAlias']
    
    def __str__(self):
        """
            A short string representation of the Contact.
            Should be called with unicode(var).
        """
        
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
    
    def getAddresses(self):
        """
            Returns a list of known addresses for this contact
        """
        
        if not self.addresses:
            sql = """
                SELECT enmAddressType, strAddress
                FROM cAddress
                WHERE intContactId = %s
                ORDER BY enmAddressType, strAddress"""
            
            self.addresses = database.executeManyToDictionary(sql, self.id)
        
        return self.addresses
        
def addContact(user, addressType, address, alias=None):
    """
        If the address is unknown, add it. In either case,
        return the address ID.
    """
    
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
    
def updateContact(user, contactId, forename, surname):
    """
        Updates the database record of a contact to the given name.
    """
    
    sql = """
        UPDATE cContact
        SET strForename = %s,
            strSurname = %s
        WHERE intId = %s
            AND strUser = %s"""
    
    database.execute(sql, (forename, surname, contactId, user)).close()
    
def getContacts(user):
    """
        Returns a list of all the contacts of the given user.
    """
    
    sql = """
        SELECT 
            c.intId AS intContactId,
            c.strForename AS strContactForename,
            c.strSurname AS strContactSurname,
            a.strAddress AS strContactBestAddress,
            a.strAlias AS strContactBestAlias
        FROM cContact c
            INNER JOIN cAddress a ON c.intId = a.intContactId
        WHERE c.strUser = %s
            AND c.bitIsMe = 0
            AND a.bitBestAddress = 1"""
    
    return [Contact(contact) for contact in database.executeManyToDictionary(sql, user)]

def mergeContacts(contacts):
    """
        Merges a list of contacts into one.
        
        Note that this operation loses data, and so cannot be undone.
    """
    
    if len(contacts) < 2:
        print 'Too few contacts given to merge'
        return
    
    moribundIds = ', '.join([str(contact.id) for contact in contacts[1:]])
    
    # Move all addresses to the alagamated contact
    sql = """
        UPDATE IGNORE cAddress
        SET intContactId = %s,
            bitBestAddress = 0
        WHERE intContactId IN (""" + moribundIds + ")"
    
    database.execute(sql, contacts[0].id).close()
    
    # Remove any addresses that are duplicates
    sql = """
        DELETE FROM cAddress
        WHERE intContactId IN (""" + moribundIds + ")"
    
    database.execute(sql).close()
    
    # Update the amalgamated contact’s surname if it hasn’t got one, but a moribund contact has.
    sql = """
        UPDATE cContact o, cContact n
        SET o.strSurname = n.strSurname
        WHERE o.intId = %s
            AND IFNULL(o.strSurname, '') = ''
            AND IFNULL(n.strSurname, '') != ''
            AND n.intId IN (""" + moribundIds + ")"
            
    database.execute(sql, contacts[0].id).close()
    
    # Update the amalgamated contact’s forename if it hasn’t got one, but a moribund contact has.
    sql = """
        UPDATE cContact o, cContact n
        SET o.strForename = n.strForename
        WHERE o.intId = %s
            AND IFNULL(o.strForename, '') = ''
            AND IFNULL(n.strForename, '') != ''
            AND n.intId IN (""" + moribundIds + ")"
            
    database.execute(sql, contacts[0].id).close()
    
    # Update the recipients of any affected messages to the amalgamated contact.
    sql = """
        UPDATE IGNORE mRecipient
        SET intContactId = %s
        WHERE intContactId IN (""" + moribundIds + ")"
        
    database.execute(sql, contacts[0].id).close()
    
    # Remove any duplicate recipients.
    sql = """
        DELETE FROM mRecipient
        WHERE intContactId IN (""" + moribundIds + ")"
    
    database.execute(sql).close()
    
    # Update the senders of any affected messages to the amalgamated contact.
    sql = """
        UPDATE mMessage
        SET intSenderId = %s
        WHERE intSenderId IN (""" + moribundIds + ")"
        
    database.execute(sql, contacts[0].id).close()
    
    # Delete all but the amalgamated contact.    
    sql = """
        DELETE FROM cContact
        WHERE intId IN (""" + moribundIds + ")"
    
    database.execute(sql).close()
    
    
    