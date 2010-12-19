import database, encryption, gatherEmail, settings
from owlExceptions import NotAuthenticatedException

class GatherData:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        
        if not self.validate():
            raise NotAuthenticatedException('The username or password was not valid')
        
    def validate(self):
        
        sql = """
            SELECT 1 FROM pUser
            WHERE strUser = %s
                AND strPassword = %s"""
        
        return database.executeOneToDictionary(sql, (self.username, self.password)) != None
    
    def gatherImap(self):
        
        sql = """
            SELECT intId, strServer, intPort, strUsername, strPassword, strEmailAddress
            FROM mAccount
            WHERE strUser = %s
                AND enmType = 'imap'"""
        
        account = database.executeOneToDictionary(sql, self.username)
        
        password = encryption.decrypt(settings.getSettings()['passwordSalt'] + self.password, account['strPassword'])
        
        encryptionPassword = settings.getSettings()['encryptionKey'] + self.password
        
        gatherEmail.getEmail(self.username, account['intId'], account['strEmailAddress'], account['strUsername'], password, \
            server=account['strServer'], port=account['intPort'], encryptUsing=encryptionPassword)
        
g = GatherData('paul', 'drowndrab59')

g.gatherImap()