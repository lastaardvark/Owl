import base64, datetime, email, email.header, imaplib, os, re, sys, time

sys.path.append(os.path.join(os.getcwd()))

import stringFunctions

class imapEmail(object):
    def __init__(self, emailAddress, server='imap.gmail.com', port=993):
        self.server = str(server)
        self.port = int(port)
        self.imap = None
        self.emailAddress = str(emailAddress)

    def login(self, username, password):
        self.imap = imaplib.IMAP4_SSL(self.server, self.port)
        rc, self.response = self.imap.login(str(username), str(password))
        return rc

    def fetchMailboxes(self):
        self.imap.select(readonly=1)
        _, response = self.imap.list()
        mailboxes = []
        for item in response:
            if not re.search('spam|draft|trash|deleted|bin', item, re.IGNORECASE):
                mailboxes.append(item.split()[-1])
        
        return mailboxes
        
    def getMailIdsFromFolder(self, folder='Inbox'):
        
        success, _ = self.imap.select(folder, readonly=1)
        
        if success == 'OK':
            _, response = self.imap.search(None, 'ALL')
            ids = [int(emailId) for emailId in response[0].split()]
        else:
            ids = []
        
        return ids
    
    def getMailIds(self):
        ids = []
        for folder in self.fetchMailboxes():
            ids += self.getMailIdsFromFolder(folder)
        
        ids = list(set(ids))
        ids.sort(reverse=True)
        return ids
    
    def decodeText(self, value):
        parts = email.header.decode_header(value)
        decoded = ''
        for part, charset in parts:
            if charset is not None:
                part = part.decode(charset)
            decoded += part
        return decoded
    
    def decodeContact(self, contact):
        alias, address = email.Utils.parseaddr(contact)
        return self.decodeText(alias), self.decodeText(address)
        
    def getMailFromId(self, id):
        print imaplib.__file__
        self.imap.select()
        _, response = self.imap.fetch(id, '(RFC822)')
        
        for responsePart in response:
            if isinstance(responsePart, tuple):
                msg = email.message_from_string(responsePart[1])
                print msg['subject']
                rtn = {}
                rtn['subject'] = email.header.decode_header(msg['subject'])[0][0]
                rtn['date'] = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate(msg['date'])))
                rtn['from'] = self.decodeContact(msg['from'])
                recipients = msg.get_all('to', []) + msg.get_all('cc', []) + msg.get_all('bcc', [])
                recipients += msg.get_all('resent-to', []) + msg.get_all('resent-cc', [])
                
                rtn['body'] = self._extractBody(msg, True)
                                
                rtn['body'] = stringFunctions.fixEncoding(rtn['body'])
                rtn['subject'] = stringFunctions.fixEncoding(rtn['subject'])
                
                recipients = email.Utils.getaddresses(recipients)
                rtn['to'] = []
                
                for alias, address in recipients:
                    rtn['to'].append((self.decodeText(alias), self.decodeText(address)))
                
                self._removeAttachments(msg)
                rtn['raw'] = stringFunctions.safeUnicode(msg.as_string())
                
                return rtn
    
    def _removeAttachments(self, msg):
        if msg.is_multipart():
            for subMessage in msg.get_payload():
                self._removeAttachments(subMessage)
        else:
            if msg.get_filename(): 
                msg.set_payload('[Attachment removed]')
    
    def _extractBody(self, msg, decode):        
        if msg.is_multipart():
            rtn = ''
            for subMessage in msg.get_payload():
                # Not an attachment
                if not subMessage.get_filename(): 
                    rtn += self._extractBody(subMessage, decode)
            return rtn
        else:
            if msg.get_filename(): 
                return ''
            else:
                return msg.get_payload(decode=decode)
    
    def logout(self):
        self.imap.logout()
