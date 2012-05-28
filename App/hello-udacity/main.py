#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi #for escaping
import re #for validating

import os
import jinja2

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

rot13_html = '''
<form method="post">
    <textarea name="text">%(cipher)s</textarea>
    <br>
    <input type="submit">
</form>
'''
signup_html = '''
<form method="post">
    <label>Username <input type="text" name="username" value="%(username)s"> </label> <div style="color:red">%(username_error)s</div>
    <label>Password <input type="password" name="password"></label> <div style="color:red">%(password_error)s</div>
    <label>Verify <input type="password" name="verify"></label> <div style="color:red">%(verify_error)s</div>
    <label>E-mail <input type="text" name="email" value="%(email)s"></label> <div style="color:red">%(email_error)s</div>
    <input type="submit">
</form>
'''

# CLASSES - CONVENIENT WAY TO GROUP TOGETHER RELATED DATA AND FUNCTIONS
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_environment.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):

    def render_front(self, title="", art="", error=""):
        self.render("index.html", title=title, art=art, error=error)

    def get(self):
        self.render_front("Your title here", "Art")

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            self.write("thanks!")
        else:
            error = "we need both a title and some artwork!"
            self.render_front("title", "art", error)

class FormHandler(webapp2.RequestHandler):  
    
    def write_form(self, error="", month="", day="", year=""):
        template_values = {"error": error,
                        "month": escape_html(month),
                        "day": escape_html(day),
                        "year": escape_html(year)
                        }
        template = jinja_environment.get_template('form.html')
        self.response.out.write(template.render(template_values))

    def get(self):
        self.write_form()


    def post(self):
        user_month = self.request.get('month')
        user_day = self.request.get('day')
        user_year = self.request.get('year')

        # SEPARATED TO KNOW WHAT USER FIRST ENTERED TO REPOPULATE FORM
        month = valid_month(user_month)
        day = valid_day(user_day)
        year = valid_year(user_year)


        if not (month and day and year): #IF NOT ALL TRUE - RESEND FORM WITH ERROR MSG
            self.write_form("That doesn't look valid.", user_month, user_day, user_year)
        else:
            self.redirect("/thanks")

class ThanksHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Thanks! That's a totally valid day.")

class Rot13Handler(webapp2.RequestHandler):
    def write_html(self, cipher=''):
        self.response.out.write(rot13_html % {"cipher": cipher})

    def get(self):
        self.write_html()

    def post(self):
        cipher = self.request.get('text')
        cipher = apply_cipher(cipher)
        self.write_html(escape_html(cipher)) #WORKED!!

class SignupHandler(webapp2.RequestHandler):
    def write_html(self, username="", email="", username_error="", password_error="",verify_error="",email_error=""):
        self.response.out.write(signup_html % {"username":username,
                                        "email":email,
                                        'username_error': username_error,
                                        'password_error': password_error,
                                        'verify_error':verify_error,
                                        'email_error': email_error}
                                        )

    def get(self):
        self.write_html()

    def post(self):
        #user_username = self.request.get('username')
        #user_password = self.request.get('password')
        #user_verify = self.request.get('verify')
        #user_email = self.request.get('email')

        username = escape_html(self.request.get('username'))
        password = escape_html(self.request.get('password'))
        verify = escape_html(self.request.get('verify'))
        email = escape_html(self.request.get('email'))

        if valid_username(username) and valid_password(password) and valid_verify(password, verify) and valid_email(email):
            self.redirect("/welcome")

        else:
            username_error, password_error, verify_error, email_error = "", "", "", ""
            if not valid_username(username):
                username_error = "Username is not valid."
            if not valid_password(password):
                password_error = "Unvalid password."
            if not valid_verify(password, verify):
                verify_error = "Passwords don't match."
            if not valid_email(email):
                email_error = "Email is not valid."

            self.write_html(username, email, username_error, password_error, verify_error, email_error)

        

class WelcomeHandler(webapp2.RequestHandler):
    def get(self):

        self.response.out.write("Welcome, %s." % username)




#URL MAPPING SECTION
app = webapp2.WSGIApplication([('/', MainHandler), ('/form', FormHandler), ('/thanks', ThanksHandler), ('/rot13', Rot13Handler), ('/signup', SignupHandler), ('/welcome', WelcomeHandler)], debug=True)


# CODE

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
def valid_day(day):
    try:
        day_num = int(day)
        if day_num >=1 and day_num <=31:
            return int(day)
        return None
    except:
        return None
# CHECKS YEAR
def valid_year(year):
    try:
        year=int(year)
        if year >= 1900 and year <= 2020:
            return year
    except:
        return None

# HTML ESCAPING
def escape_html(s):
    return cgi.escape(s, quote = True)

# FOR ROT13
def apply_cipher(s, n=13):
    new = ""
    for e in s:
        if ord(e) in range (65,91):
            new += chr( (ord(e)-65+n)%26+65 )
        elif ord(e) in range(97,123):
            new += chr( (ord(e)-97+n)%26+97 )
        else:
            new += e
    return ne

# FOR SIGNUP
#CHECKS USERNAME
user_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
password_re = re.compile(r"^.{3,20}$")
email_re = re.compile(r"[\S]+@[\S]+\.[\S]+$")

def valid_username(username):
    return user_re.match(username)

def valid_password(password):
    return password_re.match(password)

def valid_verify(password, verify):
    return password==verify

def valid_email(email):
    if email=="":
        return True
    return email_re.match(email)

