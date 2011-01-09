# coding=utf8
import database, encryption, login, settings
from owlExceptions import NotAuthenticatedException
from messageGetters.imapGetter import ImapGetter

class GatherData:
    """
        A class to gather data from all the accounts of a user
    """
    
    def __init__(self, username, password):
        """
            Takes the user’s owl credentials. Checks them (for the sake of paranoia)
            and initialises any getters for the users’s accounts.
            
            It will raise a NotAuthenticatedException if the authentication failed.
        """
        
        self.username = username
        self.password = password
        
        if not login.checkLogin(self.username, self.password):
            raise NotAuthenticatedException('The username or password was not valid')
        
        self.imapGetter = self.checkForImap()
    
    def checkForImap(self):
        """
            If the user has an IMAP account, it instantiates it.
        """
        
        sql = """
            SELECT 
                intId AS intAccountId, strServer, intPort, 
                strUsername, strPassword, strEmailAddress
            FROM mAccount
            WHERE strUser = %s
                AND enmType = 'imap'"""
        
        account = database.executeOneToDictionary(sql, self.username)
        
        if not account:
            return None
        
        # Decrypt account password
        password = settings.settings['userPasswordEncryptionSalt'] + self.password
        account['strPassword'] = encryption.decrypt(password, str(account['strPassword']))
        
        encryptionKey = settings.settings['userDataEncryptionSalt'] + self.password
        
        return ImapGetter(account, encryptionKey)
    
    def countNewMessages(self):
        """
            Returns the number of new messages accross the users’s accounts
        """
        
        if self.imapGetter:
            self.imapIds = self.imapGetter.getNewMessageIds() or []
        
        return len(self.imapIds)
    
    def getNewMessages(self, progressBroadcaster = None):
        """
            Downloads the new messages of all the users’s accounts, and stores them
            in the database.
        """
        
        if self.imapGetter:
            self.imapGetter.downloadNewMessages(self.imapIds, progressBroadcaster)
    
    def stop(self):
        """
            Stops downloading messages (after the current message has been stored)
        """
        
        if self.imapGetter:
            self.imapGetter.stop()
    