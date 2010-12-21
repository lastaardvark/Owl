import database, encryption, settings

def checkLogin(username, password):
    
    encryptedPassword = encryption.encrypt(settings.settings['loginPasswordEncryptionKey'], password)
    
    sql = """
        SELECT 1 FROM pUser
        WHERE strUser = %s
            AND strPassword = %s"""
    
    return database.executeOneToDictionary(sql, (username, encryptedPassword)) != None