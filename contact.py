# coding=utf8

import sqlite

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
        
        if 'bitContactIsMe' in fields:
            self.isMe = fields['bitContactIsMe']
        
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
    
    def getAddresses(self, db):
        """
            Returns a list of known addresses for this contact
        """
        
        if not self.addresses:
            sql = """
                SELECT strAddressType, strAddress
                FROM cAddress
                WHERE intContactId = ?
                ORDER BY strAddressType, strAddress"""
            
            self.addresses = db.executeMany(sql, self.id)
        
        return self.addresses
            
    def update(self, db):
        """
            Updates the database record of a contact to the local copy.
            Note, this does not update any addresses.
        """
        
        sql = """
            UPDATE cContact
            SET strForename = ?,
                strSurname = ?,
                strCompanyName = ?,
                bitIsPerson = ?
            WHERE intId = ?"""
        
        db.executeNone(sql, (self.forename, self.surname, self.companyName, self.isPerson, self.id))

def createContact(db, forename, surname, addressType, address, alias=None):
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
        WHERE a.strAddressType = ?
            AND a.strAddress = ?"""
    
    result = db.executeOne(sql, (addressType, address))
    
    if result == None:
        
        if forename and surname:
            
            sql = """
                INSERT INTO cContact (strForename, strSurname, bitIsPerson)
                VALUES (?, ?, 1)"""
        else:
        
            sql = """
                INSERT INTO cContact (strForename, strSurname)
                VALUES (?, ?)"""
        
        
        contactId = db.executeNoneReturnId(sql, (forename, surname))
        
        sql = """
            INSERT INTO cAddress (intContactId, strAddressType, strAddress, strAlias, bitBestAddress)
            VALUES (?, ?, ?, ?, 1)"""
        
        db.executeNone(sql, (contactId, addressType, address, alias))
    else:
        contactId = int(result['intContactId'])
    
    return contactId

def addEmptyContact(db, addressType, address, alias=None):
    return createContact(db, None, None, addressType, address, alias)

def addAddressToExitingContact(db, contactId, addressType, address, alias = None):
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
        WHERE a.strAddressType = ?
            AND a.strAddress = ?"""
    
    result = db.executeOne(sql, (addressType, address))
    
    if result:
        if int(result['intContactId']) != int(contactId):
            print "Merging contacts"
            
            mergeContacts(db, [getContactFromId(db, result['intContactId']), getContactFromId(db, contactId)])
            return result['intContactId']
    else:
        sql = """
            INSERT INTO cAddress (intContactId, strAddressType, strAddress, strAlias, bitBestAddress)
            VALUES (?, ?, ?, ?, 0)"""
        
        db.executeNone(sql, (contactId, addressType, address, alias))
    
    return contactId

def getContactFromFields(fields):
    contact = Contact(fields)
    return contact

def getContactFromId(db, id):

    sql = """
        SELECT 
            c.intId AS intContactId,
            c.strForename AS strContactForename,
            c.strSurname AS strContactSurname,
            c.strCompanyName AS strContactCompanyName,
            CAST(c.bitIsPerson AS unsigned) AS bitContactIsPerson,
            c.bitIsMe AS bitContactIsMe,
            a.strAddress AS strContactBestAddress,
            a.strAlias AS strContactBestAlias
        FROM cContact c
            INNER JOIN cAddress a ON c.intId = a.intContactId
        WHERE c.intId = ?
            AND a.bitBestAddress = 1"""
    
    contact = Contact(db.executeOne(sql, id))
    return contact
        
    
def getContacts(db):

    sql = """
        SELECT 
            c.intId AS intContactId,
            c.strForename AS strContactForename,
            c.strSurname AS strContactSurname,
            c.strCompanyName AS strContactCompanyName,
            CAST(c.bitIsPerson AS unsigned) AS bitContactIsPerson,
            c.bitIsMe AS bitContactIsMe,
            a.strAddress AS strContactBestAddress,
            a.strAlias AS strContactBestAlias
        FROM cContact c
            INNER JOIN cAddress a ON c.intId = a.intContactId
        WHERE c.bitIsMe = 0
            AND a.bitBestAddress = 1"""
    
    return [Contact(contact) for contact in db.executeMany(sql)]
    
def mergeContacts(db, contactsToMerge):
    """
        Merges a list of contacts into one.
        
        Note that this operation loses data, and so cannot be undone.
    """
    
    if len(contactsToMerge) < 2:
        print 'Too few contacts given to merge'
        return
    
    toThrow = contactsToMerge[1:]
    toKeep = contactsToMerge[0]
    
    
    for moribund in toThrow:
        if moribund.isPerson != None and toKeep.isPerson == None:
            toKeep.isPerson = moribund.isPerson
    
    for moribund in toThrow:
        if moribund.isPerson != 0 and toKeep.isPerson != 0:
            if moribund.forename and not toKeep.forename:
                toKeep.forename = moribund.forename
            if moribund.surname and not toKeep.surname:
                toKeep.surname = moribund.surname
        else:
            if moribund.companyName and not toKeep.companyName:
                toKeep.companyName = moribund.companyName
    
    toKeep.update(db)
    
    moribundIds = ', '.join([str(contact.id) for contact in toThrow])
    
    # Move all addresses to the amalgamated contact
    sql = """
        UPDATE OR IGNORE cAddress
        SET intContactId = ?,
            bitBestAddress = 0
        WHERE intContactId IN (""" + moribundIds + ")"
    
    db.executeNone(sql, contactsToMerge[0].id)
    
    # Remove any addresses that are duplicates
    sql = """
        DELETE FROM cAddress
        WHERE intContactId IN (""" + moribundIds + ")"
    
    db.executeNone(sql)
    
    # Update the recipients of any affected messages to the amalgamated contact.
    sql = """
        UPDATE OR IGNORE mRecipient
        SET intContactId = ?
        WHERE intContactId IN (""" + moribundIds + ")"
        
    db.executeNone(sql, contactsToMerge[0].id)
    
    # Remove any duplicate recipients.
    sql = """
        DELETE FROM mRecipient
        WHERE intContactId IN (""" + moribundIds + ")"
    
    db.executeNone(sql)
    
    # Update the senders of any affected messages to the amalgamated contact.
    sql = """
        UPDATE mMessage
        SET intSenderId = ?
        WHERE intSenderId IN (""" + moribundIds + ")"
        
    db.executeNone(sql, contactsToMerge[0].id)
    
    # Delete all but the amalgamated contact.    
    sql = """
        DELETE FROM cContact
        WHERE intId IN (""" + moribundIds + ")"
    
    db.executeNone(sql)
    