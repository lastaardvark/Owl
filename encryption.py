# coding=utf8
from Crypto.Cipher import AES
import base64, hashlib
import os

# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 32

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = chr(6)

# one-liner to sufficiently pad the text to be encrypted
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

def getRandomKey():
    return os.urandom(BLOCK_SIZE)

def getCipherFromKey(key):
    return AES.new(key)
    
def getCipherFromPassword(password):    
    return getCipherFromKey(hashlib.sha256(password).digest())

def encrypt(password, string):
    cipher = getCipherFromPassword(password)
    try:
        string = string.encode("utf8")
    except:  # Already UTF-8
        pass
    
    return EncodeAES(cipher, string)

def decrypt(password, string):
    cipher = getCipherFromPassword(password)
    return DecodeAES(cipher, string)