from API.view import *
from API.model import *
import datetime
import hashlib

# print(x[2].name)
CreateTweet('I will love you...babeeeee, ALWAYS', 'Lexa', date=None)

t,r = GetProfileRange('Lexa', 0, 10)
for tw in t:
    tw['date'] = str(tw['date'])
print(t)