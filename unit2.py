
#FORMS AND VALIDATION



#CHECKS MONTH
months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']
          
def valid_month(month):
    if month:
        month = month.capitalize()
        if month in months:
            return month
    return None

# CHECKS DAY
#MY VERS
def valid_day(day):
    try:
        day_num = int(day)
        if day_num >=1 and day_num <=31:
            return int(day)
        return None
    except:
        return None
#COURSE VERS
def valid_day(day):
    if day and day.isdigit():
        day = int(day)
        if day > 0 and day <=31:
            return day


# CHECKS YEAR
#MY VER
def valid_year(year):
    try:
        year=int(year)
        if year >= 1900 and year <= 2020:
            return year
    except:
        return None
#COURSE VER
def valid_year(year):
    if year and year.isdigit():
        year = int(year)
        if year >1900 and year < 2020:
            return year

# STRING SUBSTITUTION
#SIMPLE
t1 = "Hi %s"
def sub(s):
    return t1 % s

#MULT VAR
t2 = "My first name is %s and my last name is %s."
def sub_2(s1, s2):
    return t2 % (s1, s2)

#USING IDENTIFIERS AND DICTS
t3 = "My nickname is %(nickname)s. My name is %(name)s but all my friends call me %(nickname)s"
def sub_m(name, nickname):
    return t3 % {"name":name, "nickname":nickname}


# ESCAPING

#MY VER
# problems:
# dict doesn't give order to ampersand
def escape_html(s):
    escape_chars = {'>':'&gt;',
                    '<':'&lt;',
                    '"':'&quot;',
                    '&':'&amp;'}
    for char in escape_chars:
        s = s.replace(char, escape_chars[char])
    
    return s

#STEVE VER
def escape_html_2(s):
    for (i, o) in (('&','&amp;'),
                    ('>','&gt;'),
                    ('<','&lt;'),
                    ('"','&quot;')):
        s = s.replace(i, o)
    return s

#USIGN CGI MODULE
import cgi
def escape_html_3(s):
    return cgi.escape(s, quote = True)

print escape_html_3("hey <>")


# ROT 13 HOMEWORK

def apply_cipher(s, n=13):
    new = ""
    for e in s:
        if ord(e) in range (65,91):
            new += chr( (ord(e)-65+n)%26+65 )
        elif ord(e) in range(97,123):
            new += chr( (ord(e)-97+n)%26+97 )
        else:
            new += e
    return new

def caesar_cipher(letras):
    lista = []
    for n in range(0,26):
        for e in letras:
            if ord(e) in range(65,91):
                letra = chr( (ord(e) + n)%26 + 65 )
            elif ord(e) in range(97,123):
                letra = chr( (ord(e) + n)%26 + 97 )
            else:
                letra = e
            lista.append(letra)
        print ''.join(lista)
        lista =[]   



# SIGN UP HOMEWORK
import re
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)

username = "bobtheguy"

