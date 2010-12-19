import imaplib, datetime, email, time
from HTMLParser import HTMLParser

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

class imapEmail(object):
    def __init__(self, emailAddress, server='imap.gmail.com', port=993):
        self.server = str(server)
        self.port = int(port)
        self.imap = None
        self.emailAddress = str(emailAddress)
        self.mailboxes = []

    def login(self, username, password):
        self.imap = imaplib.IMAP4_SSL(self.server, self.port)
        rc, self.response = self.imap.login(str(username), str(password))
        return rc

    def fetchMailboxes(self):
        _, response = self.imap.list()
        for item in response:
            self.mailboxes.append(item.split()[-1])
        return rc

    def getMailIds(self, folder='Inbox'):
        self.imap.select(folder, readonly=1)
        _, response = self.imap.search(None, 'ALL')
        ids = [emailId for emailId in response[0].split()]
        return ids

    def getMailFromId(self, id):
        self.imap.select()
        _, response = self.imap.fetch(id, '(RFC822)')
        for responsePart in response:
            if isinstance(responsePart, tuple):
                msg = email.message_from_string(responsePart[1])
                
                rtn = {}
                rtn['subject'] = msg['subject']
                rtn['date'] = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate(msg['date'])))
                rtn['from'] = msg['from']
                rtn['to'] = msg.get_all('to', []) + msg.get_all('cc', []) + msg.get_all('bcc', [])
                rtn['to'] += msg.get_all('resent-to', []) + msg.get_all('resent-cc', [])
                
                payload = msg.get_payload()
                rtn['body'] = self._extractBody(payload)
                rtn['body'] = rtn['body'].replace('=\r\n', '')
                
                if rtn['body'].count('=0A') > 5:
                    rtn['body'] = rtn['body'].replace('=0A', '')
                    
                if rtn['body'].count('=3D') > 5:
                    rtn['body'] = rtn['body'].replace('=3D', '=')
                                
                return rtn
                
    def _extractBody(self, payload):
        if isinstance(payload, str):
            return payload
        else:
            return '/n'.join([self._extractBody(part.get_payload()) for part in payload])
    
    def _stripHtml(self, text):
        stripper = HtmlStripper()
        stripper.feed(text)
        return stripper.get_data()
    
    def logout(self):
        self.imap.logout()
