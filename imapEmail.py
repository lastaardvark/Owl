import imaplib, datetime, email, email.header, re, time
from HTMLParser import HTMLParser
import base64
import chardet

class HtmlStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
    
def safe_unicode(obj, *args):
    """ return the unicode representation of obj """
    try:
        return unicode(obj, *args)
    except UnicodeDecodeError:
        # obj is byte string
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)

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
        
    def getMailFromId(self, id):
        self.imap.select()
        _, response = self.imap.fetch(id, '(RFC822)')
        for responsePart in response:
            if isinstance(responsePart, tuple):
                msg = email.message_from_string(responsePart[1])
                
                rtn = {}
                rtn['subject'] = email.header.decode_header(msg['subject'])[0][0]
                
                rtn['date'] = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate(msg['date'])))
                rtn['from'] = email.header.decode_header(msg['from'])[0][0]
                rtn['to'] = msg.get_all('to', []) + msg.get_all('cc', []) + msg.get_all('bcc', [])
                rtn['to'] += msg.get_all('resent-to', []) + msg.get_all('resent-cc', [])
                
                rtn['body'] = self._extractBody(msg, True)                
                rtn['raw'] = safe_unicode(msg.as_string())
                                
                if isinstance(rtn['body'], str):
                    encodingGuess = chardet.detect(rtn['body'])['encoding']
                    print encodingGuess
                    if encodingGuess and encodingGuess != 'UTF-8' and encodingGuess != 'ASCII':
                        rtn['body'] = rtn['body'].decode(encodingGuess)
                
                rtn['from'] = safe_unicode(rtn['from'])
                rtn['body'] = safe_unicode(rtn['body'])
                rtn['subject'] = safe_unicode(rtn['subject'])
                
                return rtn
                
    def _extractBody(self, msg, decode):        
        if msg.is_multipart():
            rtn = ''
            for subMessage in msg.get_payload():
                if not subMessage.get_filename(): # Not an attachment
                    rtn += self._extractBody(subMessage, decode)
            return rtn
        else:
            if msg.get_filename(): # Not an attachment
                return ''
            else:
                return msg.get_payload(decode=decode)
               
    def _stripHtml(self, text):
        stripper = HtmlStripper()
        stripper.feed(text)
        return stripper.get_data()
    
    def logout(self):
        self.imap.logout()
