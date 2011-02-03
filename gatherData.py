# coding=utf8
import account, login, settings
from sqlite import Sqlite
from owlExceptions import NotAuthenticatedException
from messageGetters.imapGetter import ImapGetter
from messageGetters.iPhoneGetter import IPhoneGetter
from messageGetters.imGetter import IMGetter

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
        db = Sqlite(self.username)
        
        self.accountDecriptionKey = settings.settings['userPasswordEncryptionSalt'] + password
        self.encryptionKey = settings.settings['userDataEncryptionSalt'] + password
        
        if not login.checkLogin(username, password):
            raise NotAuthenticatedException('The username or password was not valid')
        
        self.imapGetters = self.checkForImap(db)
        self.iPhoneGetters = self.checkForIPhone(db)
        self.imLogGetter = self.checkForIMLogs(db)
        
        db.close()
    
    def checkForImap(self, db):
        """
            If the user has an IMAP account, it instantiates it.
        """
        
        accounts = account.getImapAccounts(db, self.accountDecriptionKey)
        
        if accounts:
            return [ImapGetter(imap, self.encryptionKey) for imap in accounts]
        
        return None
    
    def checkForIPhone(self, db):
        """
            If the user has an iPhone account, it instantiates it.
        """
        
        accounts = account.getSmsAccounts(db)
        
        if accounts:
            return [IPhoneGetter(db, iPhone, self.encryptionKey) for iPhone in accounts]
        
        return None
    
    def checkForIMLogs(self, db):
        
        if settings.knownIMLogPaths:
            return IMGetter(db, self.encryptionKey)
    
    def refreshNewMessageCounts(self, db):
        
        for getter in self.imapGetters:
            getter.getNewMessageIds(db)
        
        for getter in self.iPhoneGetters:
            getter.getNewMessageIds(db)
        
        if self.imLogGetter:
            self.imLogGetter.getNewMessageIds(db)
        
    def getAllNewMessageCounts(self):
        
        imapCount = 0
        iPhoneCount = 0
        imLogCount = 0
        
        rtn = []
        
        for getter in self.imapGetters:
            imapCount += len(getter.idsToFetch)
        
        if self.imapGetters:
            rtn.append({'type': 'IMAP emails', 'number': imapCount})

        for getter in self.iPhoneGetters:
            iPhoneCount += len(getter.idsToFetch)
        
        if self.iPhoneGetters:
            rtn.append({'type': 'iPhone messages', 'number': iPhoneCount})
            
        if self.imLogGetter:
            imLogCount = len(self.imLogGetter.idsToFetch)
            rtn.append({'type': 'IM logs', 'number': imLogCount})
            
        total = imapCount + iPhoneCount + imLogCount
        
        rtn.append({'type': 'All', 'number': total})
        
        return rtn
    
    def countNewMessages(self, type = 'All'):
        
        allTypes = self.getAllNewMessageCounts()
        
        for eachType in allTypes:
            if eachType['type'] == type:
                return eachType['number']
    
    def getNewMessages(self, type = 'All', progressBroadcaster = None):
        """
            Downloads the new messages of all the users’s accounts, and stores them
            in the database.
        """
        
        db = Sqlite(self.username)
        
        if type in ('All', 'iPhone messages'):
            for getter in self.iPhoneGetters:
                getter.downloadNewMessages(db, progressBroadcaster)
        
        if type in ('All', 'IM logs'):
            if self.imLogGetter:
                self.imLogGetter.downloadNewConversations(db, progressBroadcaster)
        
        if type in ('All', 'IMAP emails'):
            for getter in self.imapGetters:
                getter.downloadNewMessages(db, progressBroadcaster)
                
        db.close()
    
    def stop(self):
        """
            Stops downloading messages (after the current message has been stored)
        """
        
        for getter in self.imapGetters:
            getter.stop()
            
        for getter in self.iPhoneGetters:
            getter.stop()
        
        if self.imLogGetter:
            self.imLogGetter.stop()
    