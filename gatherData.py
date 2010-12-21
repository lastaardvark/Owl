import database, encryption, login, settings
from owlExceptions import NotAuthenticatedException
from messageGetters.imapGetter import ImapGetter

class GatherData:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        
        if not login.checkLogin(self.username, self.password):
            raise NotAuthenticatedException('The username or password was not valid')
        
        self.imapGetter = self.checkForImap()
    
    def checkForImap(self):
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
        account['strPassword'] = encryption.decrypt(settings.settings['userPasswordEncryptionSalt'] + self.password, str(account['strPassword']))
        
        encryptionKey = settings.settings['userDataEncryptionSalt'] + self.password
        
        return ImapGetter(self.username, account, encryptionKey)
    
    def countNewMessages(self):
        
        if self.imapGetter:
            self.imapIds = self.imapGetter.getNewMessageIds() or []
        
        return len(self.imapIds)
    
    def getNewMessages(self, progressBroadcaster = None):
        
        if self.imapGetter:
            self.imapGetter.downloadNewMessages(self.imapIds, progressBroadcaster)