# coding=utf8

import HTMLParser, re
import chardet

class HtmlStripper(HTMLParser.HTMLParser):
    """
        A class to remove HTML tags from text.
    """
    
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def stripTags(html):
    """
        Remove HTML tags from text
    """
    
    s = HtmlStripper()
    try:
        s.feed(html)
        return s.get_data()
    except HTMLParser.HTMLParseError:
        return re.sub("<\/?[^>]*>", "", html)
  
def safeUnicode(obj):
    """
        Returns the unicode representation of obj.
    """
    
    try:
        return unicode(obj)
    except UnicodeDecodeError:
        # obj is byte string
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)

def fixEncoding(string):
    """
        Attempts to guess the encoding of the given string.
        
        If the string encoding is not UTF-8 or ASCII, it attempts to decode it,
    """
    
    if isinstance(string, str):
        encodingGuess = chardet.detect(string)['encoding']
        if encodingGuess == 'EUC-TW':
            return safeUnicode(string)
        if encodingGuess and encodingGuess != 'UTF-8' and encodingGuess != 'ASCII':
            return string.decode(encodingGuess)
    return string

def formatInt(number):
    """
        Returns the number as a string with each three digits separated
        by a comma.
    """
    
    number = str(number)
    
    components = []
    
    start = len(number) % 3
    
    if start != 0:
        components.append(number[0:start])
        
    for n in range(start, len(number), 3):
        components.append(number[n: n + 3])
    
    return ",".join(components)