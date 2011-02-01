# coding=utf8

import os, sqlite3

def executeOneToDictionary(connection, sql, parameters = None):
    cursor = connection.cursor()
    
    if parameters:
            
        if type(parameters) != type((1,)):
            parameters = (parameters, )
            
        cursor.execute(sql, parameters)
    else:
        cursor.execute(sql)
    
    data = cursor.fetchone()

    if data == None :
        cursor.close()
        return None
        
    desc = cursor.description
    
    cursor.close()
    
    dict = {}

    for (name, value) in zip(desc, data) :
        dict[name[0]] = value

    return dict
    
def executeManyToDictionary(connection, sql, parameters=None):
    cursor = connection.cursor()
    
    if parameters:
    
        if type(parameters) != type((1,)):
            parameters = (parameters, )
            
        cursor.execute(sql, parameters)
    else:
        cursor.execute(sql)
    
    table = cursor.fetchall()

    if table == None:
        cursor.close()
        return None
        
    desc = cursor.description
    
    cursor.close()
    
    rtn = []
    
    for row in table:
        dict = {}
    
        for (name, value) in zip(desc, row):
            dict[name[0]] = value
        
        rtn.append(dict)
        
    return rtn
    
def executeNonQuery(connection, sql, parameters = None):
    cursor = connection.cursor()
    
    if parameters:            
        if type(parameters) != type((1,)):
            parameters = (parameters, )
            
        cursor.execute(sql, parameters)
    else:
        cursor.execute(sql)
    
    connection.commit()
    cursor.close()
    
def executeNonQueryAndReturnId(connection, sql, parameters = None):
    cursor = connection.cursor()
    
    if parameters:            
        if type(parameters) != type((1,)):
            parameters = (parameters, )
            
        cursor.execute(sql, parameters)
    else:
        cursor.execute(sql)
    
    id = cursor.lastrowid
    
    connection.commit()
    cursor.close()
    
    return id
    
class Sqlite:
    def __init__(self, user, create=False):
        if create:
            self.createSchema(user)
        else:
            self.connect(user)
    
    def executeOne(self, sql, parameters = None):
        return executeOneToDictionary(self.connection, sql, parameters)
        
    def executeMany(self, sql, parameters = None):
        return executeManyToDictionary(self.connection, sql, parameters)
        
    def executeNone(self, sql, parameters = None):
        return executeNonQuery(self.connection, sql, parameters)
        
    def executeNoneReturnId(self, sql, parameters = None):
        return executeNonQueryAndReturnId(self.connection, sql, parameters)
        
    def connect(self, user):
        
        path = os.path.expanduser('~/Library/Application Support/Owl/')
        path = os.path.join(path, user)
                    
        file = os.path.join(path, 'owldb')
        
        self.connection = sqlite3.connect(file)
        
    def close(self):
        self.connection.commit()
        self.connection.close()
        self.connection == None
    
    def createSchema(self, user):
        
        path = os.path.expanduser('~/Library/Application Support/Owl/')
        
        if not os.path.exists(path):
            os.mkdir(path)
        
        path = os.path.join(path, user)
        
        if not os.path.exists(path):
            os.mkdir(path)
        
        file = os.path.join(path, 'owldb')
        
        self.connection = sqlite3.connect(file)
        
        sql = "DROP TABLE IF EXISTS mEmail"
        self.executeNone(sql)
        
        sql = "DROP TABLE IF EXISTS mSms"
        self.executeNone(sql)
        
        sql = "DROP TABLE IF EXISTS mRecipient"
        self.executeNone(sql)
        
        sql = "DROP TABLE IF EXISTS mMessage"
        self.executeNone(sql)
        
        sql = "DROP TABLE IF EXISTS cAddress"
        self.executeNone(sql)
        
        sql = "DROP TABLE IF EXISTS cContact"
        self.executeNone(sql)
        
        sql = "DROP TABLE IF EXISTS aSmsAccount"
        self.executeNone(sql)
        
        sql = "DROP TABLE IF EXISTS aEmailAccount"
        self.executeNone(sql)
        
        sql = "DROP TABLE IF EXISTS aAccount"
        self.executeNone(sql)
        
        sql = """
            CREATE TABLE aAccount (
                intId          integer PRIMARY KEY AUTOINCREMENT,
                strType        text    NOT NULL,
                strUserAddress text
            );"""
        
        self.executeNone(sql)
        
        sql = """
            CREATE TABLE aEmailAccount (
                intAccountId   int   NOT NULL,
                strServer      text  NOT NULL,
                intPort        int   NOT NULL,
                strUsername    text  NOT NULL,
                strPassword    text  NOT NULL,
                
                CONSTRAINT aEmailAccount_PK PRIMARY KEY (intAccountId),
                CONSTRAINT aEmailAccount_aAccount FOREIGN KEY (intAccountId)
                    REFERENCES aAccount (intId)
            );"""
            
        self.executeNone(sql)
        
        sql = """
            CREATE TABLE aSmsAccount (
                intAccountId      int   NOT NULL,
                strDefaultCountry text  NOT NULL, 
                
                CONSTRAINT aSmsAccount_PK PRIMARY KEY (intAccountId),
                CONSTRAINT aSmsAccount_aAccount FOREIGN KEY (intAccountId)
                    REFERENCES aAccount (intId)
            );"""
            
        self.executeNone(sql)
        
        sql = """
            CREATE TABLE cContact (
                intId             integer PRIMARY KEY AUTOINCREMENT,
                bitIsMe           int     NOT NULL DEFAULT 0,
                strForename       text    DEFAULT NULL,
                strSurname        text    DEFAULT NULL,
                strCompanyName    text    DEFAULT NULL,
                bitIsPerson       int     DEFAULT NULL
            );"""
            
        self.executeNone(sql)
        
        sql = """
            CREATE TABLE cAddress (
                intContactId      int  NOT NULL,
                strAddressType    text NOT NULL,
                strAddress        text NOT NULL,
                strAlias          text DEFAULT NULL,
                bitBestAddress     int  NOT NULL DEFAULT 0,
                
                CONSTRAINT cAddress_PK PRIMARY KEY (intContactId, strAddressType, strAddress),
                CONSTRAINT cAddress_cContact_FK FOREIGN KEY (intContactId)
                    REFERENCES cContact (intId)
            );"""
            
        self.executeNone(sql)
        
        sql = """
            CREATE TABLE mMessage (
                intId            integer PRIMARY KEY AUTOINCREMENT,
                intAccountId     int     NOT NULL,
                intSenderId      int     NOT NULL,
                datHappened      text    NOT NULL,
                strSummary       text    NOT NULL,
                
                CONSTRAINT mMessage_cContact_FK FOREIGN KEY (intSenderId)
                    REFERENCES cContact (intId),
                CONSTRAINT mMessage_aAccount_FK FOREIGN KEY (intAccountId)
                    REFERENCES aAccount (intId)
            );"""
            
        self.executeNone(sql)
        
        sql = """
            CREATE TABLE mRecipient (
                intMessageId   int  NOT NULL,
                intContactId   int  NOT NULL,
                
                CONSTRAINT mRecipient_PK PRIMARY KEY (intMessageId, intContactId),
                CONSTRAINT mRecipient_cContact_FK FOREIGN KEY (intContactId)
                    REFERENCES cContact (intId),
                CONSTRAINT mRecipient_mMessage_FK FOREIGN KEY (intMessageId)
                    REFERENCES mMessage (intId)
            );"""
            
        self.executeNone(sql)
        
        sql = """
            CREATE TABLE mEmail (
                intMessageId     int  NOT NULL,
                intRemoteId      int  NOT NULL,
                strSubject       text NOT NULL,
                strBodyPlainText text DEFAULT NULL,
                strBodyHtml      text DEFAULT NULL,
                strRaw           text DEFAULT NULL,
                
                CONSTRAINT mEmail_PK PRIMARY KEY (intMessageId),
                CONSTRAINT mEmail_mMessage_FK FOREIGN KEY (intMessageId)
                    REFERENCES mMessage (intId)
            );"""
            
        self.executeNone(sql)
        
        sql = """
            CREATE TABLE mSms (
                intMessageId     int  NOT NULL,
                intRemoteId      int  NOT NULL,
                strText          text NOT NULL,
                
                CONSTRAINT mSms_PK PRIMARY KEY (intMessageId),
                CONSTRAINT mSms_mMessage_FK FOREIGN KEY (intMessageId)
                    REFERENCES mMessage (intId)
            );"""
            
        self.executeNone(sql)
        
        sql = "INSERT INTO aAccount (strType, strUserAddress) VALUES ('imap', 'admin@pjroberts.com')"
        id = self.executeNoneReturnId(sql)
        
        sql = "INSERT INTO aEmailAccount (intAccountId, strServer, intPort, strUsername, strPassword) VALUES (?, 'imap.gmail.com', 993, 'admin@pjroberts.com', '1efXp6I4MzGBdhsq9gh/8eDmJx/UKfAUb81vPUVCsCY=')"
        self.executeNone(sql, id)
        
        sql = "INSERT INTO aAccount (strType, strUserAddress) VALUES ('iPhone SMS', '+447985577384')"
        id = self.executeNoneReturnId(sql)
        
        sql = "INSERT INTO aSmsAccount (intAccountId, strDefaultCountry) VALUES (?, 'uk')"
        self.executeNone(sql, id)
        
        sql = "INSERT INTO cContact (bitIsMe, strForename, strSurname) VALUES (1, 'Paul', 'Roberts')"
        id = self.executeNoneReturnId(sql)
        
        sql = "INSERT INTO cAddress(intContactId, strAddressType, strAddress, bitBestAddress, strAlias) VALUES (?, 'email', 'proberts84@gmail.com', 0, 'Paul Roberts')"
        self.executeNone(sql, id)
        
        sql = "INSERT INTO cAddress(intContactId, strAddressType, strAddress, bitBestAddress, strAlias) VALUES (?, 'email', 'paul@pjroberts.com', 1, 'Paul Roberts')"
        self.executeNone(sql, id)
        
        sql = "INSERT INTO cAddress(intContactId, strAddressType, strAddress, bitBestAddress, strAlias) VALUES (?, 'email', 'admin@pjroberts.com', 0, 'Paul Roberts')"
        self.executeNone(sql, id)
        
        sql = "INSERT INTO cAddress(intContactId, strAddressType, strAddress, bitBestAddress, strAlias) VALUES (?, 'phone', '+447985577384', 0, NULL)"
        self.executeNone(sql, id)
        