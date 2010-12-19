import database

def checkLogin(username, password):
    
    sql = """
        SELECT 1 FROM pUser
        WHERE strUser = %s
            AND strPassword = %s"""
    
    return database.executeOneToDictionary(sql, (username, password)) != None