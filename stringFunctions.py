from HTMLParser import HTMLParser
import chardet

class HtmlStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def stripTags(html):
    s = HtmlStripper()
    try:
        s.feed(html)
        return s.get_data()
    except HTMLParser.HTMLParseError:
        return re.sub("<\/?[^>]*>", "", html)
  
def safeUnicode(obj, *args):
    """ return the unicode representation of obj """
    try:
        return unicode(obj, *args)
    except UnicodeDecodeError:
        # obj is byte string
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)

def fixEncoding(string):
    if isinstance(string, str):
        encodingGuess = chardet.detect(string)['encoding']
        if encodingGuess and encodingGuess != 'UTF-8' and encodingGuess != 'ASCII':
            return string.decode(encodingGuess)
