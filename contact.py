# coding=utf8

import database

_contacts = {}
_user = ''

class Contact:
    
    def __init__(self, fields):
        """
            Initializes a new Contact using a dictionary
            of database fields.
        """
        
        self.forename = None
        self.surname = None
        self.companyName = None
        self.isPerson = None
        self.bestAddress = None
        self.bestAlias = None
        
        self.id = int(fields['intContactId'])
        
        if 'strContactForename' in fields:
            self.forename = fields['strContactForename']
        if 'strContactSurname' in fields:
            self.surname = fields['strContactSurname']
        if 'strContactCompanyName' in fields:
            self.companyName = fields['strContactCompanyName']
        if 'bitContactIsPerson' in fields:
            self.isPerson = fields['bitContactIsPerson']
            
            if self.isPerson == 1:
                self.isPerson = True
            elif self.isPerson == 0:
                self.isPerson = False
            # Otherwise leave as None
        
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
        
        isPerson = self.isPerson
        if self.isPerson == None:
            isPerson = True
        
        if not isPerson and self.companyName:
            return self.companyName
        
        if isPerson and self.forename and self.surname:
            return self.forename + ' ' + self.surname
        
        if isPerson and self.surname:
            return '? ' + self.surname
            
        if isPerson and self.forename:
            return self.forename + ' ?'
            
        if self.bestAlias:
            return self.bestAlias
                    
        if self.bestAddress:
            return self.bestAddress
            
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
            
    def update(self):
        """
            Updates the database record of a contact to the local copy.
            Note, this does not update any addresses.
        """
        
        sql = """
            UPDATE cContact
            SET strForename = %s,
                strSurname = %s,
                strCompanyName = %s,
                bitIsPerson = %s
            WHERE intId = %s"""
        
        database.execute(sql, (self.forename, self.surname, self.companyName, self.isPerson, self.id)).close()

def initialize(user):
    global _user
    _user = user
    refresh()

def createContact(forename, surname, addressType, address, alias=None):
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
    
    result = database.executeOneToDictionary(sql, (_user, addressType, address))
    
    if result == None:
        
        sql = """
            INSERT INTO cContact (strUser, strForename, strSurname)
            VALUES (%s, %s, %s)"""
        
        cursor = database.execute(sql, (_user, forename, surname))
        
        contactId = cursor.lastrowid
        cursor.close()
        
        sql = """
            INSERT INTO cAddress (intContactId, enmAddressType, strAddress, strAlias, bitBestAddress)
            VALUES (%s, %s, %s, %s, 1)"""
        
        database.execute(sql, (contactId, addressType, address, alias)).close()
    else:
        contactId = int(result['intContactId'])
    
    _contacts[contactId] = Contact({
        'strContactForename': forename,
        'strContactSurname': surname,
        'intContactId': contactId, 
        'strContactBestAddress': address,
        'strContactBestAlias': alias})
    
    return contactId

def addEmptyContact(addressType, address, alias=None):
    return createContact(None, None, addressType, address, alias)

def addAddressToExitingContact(contactId, addressType, address, alias = None):
    """
        Adds the given address to the given contact. This addition may cause
        the contact to merge with another (if the address is already known).
        We therefore return the ID of the contact that now has the address.
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
    
    result = database.executeOneToDictionary(sql, (_user, addressType, address))
    
    if result:
        if int(result['intContactId']) != int(contactId):
            print "Merging contacts"
            mergeContacts([getContactFromId(result['intContactId']), getContactFromId(contactId)])
            return result['intContactId']
    else:
        sql = """
            INSERT INTO cAddress (intContactId, enmAddressType, strAddress, strAlias, bitBestAddress)
            VALUES (%s, %s, %s, %s, 1)"""
        
        database.execute(sql, (contactId, addressType, address, alias)).close()
    
    return contactId

def getContactFromFields(fields):
    contact = Contact(fields)
    _contacts[contact.id] = contact
    return contact

def getContactFromId(id):
    id = int(id)
    
    if id in _contacts:
        return _contacts[id]
    else:                       # The user, for example
        sql = """
            SELECT 
                c.intId AS intContactId,
                c.strForename AS strContactForename,
                c.strSurname AS str_contactsurname,
                c.strCompanyName AS strContactCompanyName,
                CAST(c.bitIsPerson AS unsigned) AS bitContactIsPerson,
                a.strAddress AS strContactBestAddress,
                a.strAlias AS strContactBestAlias
            FROM cContact c
                INNER JOIN cAddress a ON c.intId = a.intContactId
            WHERE c.intId = %s
                AND a.bitBestAddress = 1"""
        
        contact = Contact(database.executeOneToDictionary(sql, id))
        _contacts[contact.id] = contact
        return contact
        
    
def getContacts():
    return _contacts.values()

def refresh():
    """
        Refreshes the contact list to match the database.
    """
    global _contacts

    sql = """
        SELECT 
            c.intId AS intContactId,
            c.strForename AS strContactForename,
            c.strSurname AS strContactSurname,
            c.strCompanyName AS strContactCompanyName,
            CAST(c.bitIsPerson AS unsigned) AS bitContactIsPerson,
            a.strAddress AS strContactBestAddress,
            a.strAlias AS strContactBestAlias
        FROM cContact c
            INNER JOIN cAddress a ON c.intId = a.intContactId
        WHERE c.strUser = %s
            AND c.bitIsMe = 0
            AND a.bitBestAddress = 1"""
    
    contacts = [Contact(contact) for contact in database.executeManyToDictionary(sql, _user)]
    
    _contacts = dict([[contact.id, contact] for contact in contacts])
    
def mergeContacts(contactsToMerge):
    """
        Merges a list of contacts into one.
        
        Note that this operation loses data, and so cannot be undone.
    """
    
    if len(contactsToMerge) < 2:
        print 'Too few contacts given to merge'
        return
    
    moribundIds = ', '.join([str(contact.id) for contact in contactsToMerge[1:]])
    
    # Move all addresses to the amalgamated contact
    sql = """
        UPDATE IGNORE cAddress
        SET intContactId = %s,
            bitBestAddress = 0
        WHERE intContactId IN (""" + moribundIds + ")"
    
    database.execute(sql, contactsToMerge[0].id).close()
    
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
            AND n.bitIsPerson = 1
            AND o.bitIsPerson = 1
            AND n.intId IN (""" + moribundIds + ")"
            
    database.execute(sql, contactsToMerge[0].id).close()
    
    # Update the amalgamated contact’s forename if it hasn’t got one, but a moribund contact has.
    sql = """
        UPDATE cContact o, cContact n
        SET o.strForename = n.strForename
        WHERE o.intId = %s
            AND IFNULL(o.strForename, '') = ''
            AND IFNULL(n.strForename, '') != ''
            AND n.bitIsPerson = 1
            AND o.bitIsPerson = 1
            AND n.intId IN (""" + moribundIds + ")"
            
    database.execute(sql, contactsToMerge[0].id).close()
    
    # Update the amalgamated contact’s company name if it hasn’t got one, but a moribund contact has.
    sql = """
        UPDATE cContact o, cContact n
        SET o.strCompanyName = n.strCompanyName
        WHERE o.intId = %s
            AND IFNULL(o.strCompanyName, '') = ''
            AND IFNULL(n.strCompanyName, '') != ''
            AND n.bitIsPerson = 0
            AND n.intId IN (""" + moribundIds + ")"
            
    database.execute(sql, contactsToMerge[0].id).close()
    
    # Update the amalgamated contact’s type if it hasn’t got one, but a moribund contact has.
    sql = """
        UPDATE cContact o, cContact n
        SET o.bitIsPerson = n.bitIsPerson
        WHERE o.intId = %s
            AND o.bitIsPerson IS NULL
            AND n.bitIsPerson IS NOT NULL
            AND n.intId IN (""" + moribundIds + ")"
            
    database.execute(sql, contactsToMerge[0].id).close()
    
    # Update the recipients of any affected messages to the amalgamated contact.
    sql = """
        UPDATE IGNORE mRecipient
        SET intContactId = %s
        WHERE intContactId IN (""" + moribundIds + ")"
        
    database.execute(sql, contactsToMerge[0].id).close()
    
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
        
    database.execute(sql, contactsToMerge[0].id).close()
    
    # Delete all but the amalgamated contact.    
    sql = """
        DELETE FROM cContact
        WHERE intId IN (""" + moribundIds + ")"
    
    database.execute(sql).close()
    
    refresh()
    