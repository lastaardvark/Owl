import MySQLdb, settings, threading


local = threading.local()

def getDatabaseName():
    dbSettings = settings.getSettings()
    return dbSettings['database']
    
def getCursor():
    MySQLdb.use_unicode = True
    
    if '_Conn' not in local.__dict__ or local._Conn == None:
        dbSettings = settings.getSettings()
        local._Conn = MySQLdb.connect( host = dbSettings['server'], user = dbSettings['user'], passwd = dbSettings['password'],  db = dbSettings['database'], charset="utf8" )

    return local._Conn.cursor()
 
def close():
    if local._Conn != None:
        local._Conn.close()
        local._Conn = None
    
    
def execute(sql, parameters = None):
    cursor = getCursor()
    tries = 0
    done = False
    if not sql.startswith('CALL '):
        sql += '; commit;'

    while not done and tries < 5:
        try:
            cursor.execute(sql, parameters)
            done = True
        except MySQLdb.OperationalError as err:
            tries += 1
            try:
                cursor.close()
            except:
                pass
            
            _Conn = None
            cursor = getCursor()
        except MySQLdb.ProgrammingError as err:
            tries += 1
            try:
                cursor.close()
            except:
                pass
            _Conn = None
            cursor = getCursor()
    
    if not done:
        cursor.execute(sql, parameters)
        
    return cursor
    
def executeOneToDictionary(sql, parameters = None):
    cursor = execute(sql, parameters)
    
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
    
def executeManyToDictionary(sql, parameters=None):
    cursor = execute(sql, parameters)
    
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