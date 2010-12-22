import os, sys

sys.path.append(os.path.join(os.getcwd()))

from message import Message

class Email(Message):
    
    def __init__(self, fields):
        Message.__init__(self, fields)
        
        self.remoteId = fields["intEmailRemoteId"]
        self.subject = fields["strEmailSubject"]
        self.body = fields["strEmailBody"]