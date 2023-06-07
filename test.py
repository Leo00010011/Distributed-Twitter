from API.view import *
from API.model import *
import datetime
import hashlib

# print(x[2].name)
# CreateTweet('I will love you...babeeeee, ALWAYS', 'Lexa', date=None)
x = hashlib.sha256(b'Lexa').hexdigest()
h = int(x,16)
print(x)
print(h)