# coding=utf8

from autoCompleteListBox import AutoCompleteListBox

class MessageListBox(AutoCompleteListBox):
    
    def __init__(self, window, listData):
        
        AutoCompleteListBox.__init__(self, window, listData)
        self.unfilteredList = []
        self.unfilteredSublist = []
    
    def removeFilter(self):
        self.subList = self.unfilteredSublist
        self.listData = self.unfilteredList
        
        self.listModel.replaceList(self.subList)
    
    def filterByContact(self, contact):
        if self.unfilteredList:
            self.removeFilter()
        self.unfilteredSublist = self.subList
        self.unfilteredList = self.listData
        
        self.listData = [item for item in self.listData if self._messageReferencesContact(item[1], contact)]
        self.subList = [item for item in self.subList if item in self.listData]
        
        self.listModel.replaceList(self.subList)
            
    def _messageReferencesContact(self, message, contact):
        
        if message.sender.id == contact.id:
            return True
        
        for recipient in message.recipients:
            if recipient.id == contact.id:
                return True
        
        return False