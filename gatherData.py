import database, encryption, gatherEmail, login, settings
from owlExceptions import NotAuthenticatedException

class GatherData:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        
        if not login.checkLogin(self.username, self.password):
            raise NotAuthenticatedException('The username or password was not valid')
    
    def gatherImap(self):
        
        sql = """
            SELECT intId, strServer, intPort, strUsername, strPassword, strEmailAddress
            FROM mAccount
            WHERE strUser = %s
                AND enmType = 'imap'"""
        
        account = database.executeOneToDictionary(sql, self.username)
        
        password = encryption.decrypt(settings.getSettings()['userPasswordEncryptionSalt'] + self.password, str(account['strPassword']))
        
        encryptionPassword = settings.getSettings()['userDataEncryptionSalt'] + self.password
        
        gatherEmail.getEmail(self.username, account['intId'], account['strEmailAddress'], account['strUsername'], password, \
            server=account['strServer'], port=account['intPort'], encryptUsing=encryptionPassword)
