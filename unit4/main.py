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
import os
import webapp2
import jinja2
import hmac
import re
import random
import string
import hashlib

# for logging
import logging

from google.appengine.ext import db

SECRET = "imsosecret"

def hash_str(s):
    ''' Return the MD5-hash of a string'''
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    ''' Takes a string and returns a string of the format s,HASH'''
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):    
    ''' Takes string of format s,HASH and returns s if hash_str(s) == HASH, otherwise None'''
    s = h[:h.rfind("|")] # finds last comma with .rfind() before HASH
    if make_secure_val(s) == h:
        return s

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

# DATABASE
class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty(required = True)

class Handler(webapp2.RequestHandler):
    # function that simplifies sending requests:
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    # function that renders string of template:
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    # takes both functions above and joins them
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    def get(self):
    	self.response.headers['Content-Type'] = 'text/plain'
    	# creates a temporary variable for visits
        visits = 0
        
        # tries to get cookie with number of previous visits
        visit_cookie_str = self.request.cookies.get('visits')
        # if page has been visited before add number of previous visits to temp var.
        # if not, nothing will be added and the var will be 0, as expected
    	if visit_cookie_str: # checks if user has been to page before
            # checks return hashed val to see if cookies were changed
            cookie_val = check_secure_val(visit_cookie_str)
            # if they weren't, use them. else, start over form 0
            if cookie_val:
                visits = int(cookie_val)

        #increment no of visits by 1 - that's the current visit
    	visits +=1

        # pass on the new value of visits to a cookie header to be served next time page is visited
        new_cookie_val = make_secure_val(str(visits))

    	self.response.headers.add_header('Set-Cookie', 'visits=%s' % new_cookie_val)

    	if visits > 10000:
    		self.write("You are so cool dude")
    	else:
	    	self.write("You have been here %s times!" % visits)

class SignupHandler(Handler):
    def get(self):
        self.render("form.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        errors = {}
        check_errors(errors, username, password, verify, email)
        logging.info("Errors are %s" % len(errors))
        if len(errors) == 0:
            # Creating user in db
            pw_hash = make_pw_hash(username, password)
            logging.info("Password hash is %s" % pw_hash)
            u = User(username=username, password=pw_hash, email=email)
            u.put()
            user_id = u.key().id()
            cookie_str = make_secure_val(str(user_id))
            # self.response.headers.add_header('Set-Cookie', 'user=%s' % cookie_str)
            self.response.set_cookie('user', cookie_str)
            logging.info("Cookie set. Trying to redirect.")
            self.redirect('/welcome')

        else:
            errors['username'] = username
            errors['email'] = email
            self.render("form.html", **errors)

class LoginHandler(Handler):
    def get(self):
        self.render("login.html")
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        params = {}

        u = User.gql("WHERE username = :1", username).get()
        logging.info('%s' % u.username)
        logging.info('%s' % u.password)

        if u:
            if valid_pw(username, password, u.password):
                set_login_cookie(self, u)
                self.redirect("/welcome")
            else:
                params['error_password'] = "Invalid Password"
        else:
            params['error_username'] = "Invalid Username"
        params['username'] = username
        self.render("login.html", **params)

class LogoutHandler(Handler):
    def get(self):
        self.response.set_cookie("user", "")
        self.redirect('/signup')

class WelcomeHandler(Handler):
    def get(self):
        logging.info("Redirect ok. Checking cookie values.")
        user_cookie_str = self.request.cookies.get('user')
        logging.info("Cookie is %s" % user_cookie_str)
        user_id = check_secure_val(user_cookie_str)
        logging.info("User ID is %s" % user_id)
        if user_id:
            logging.info("Cookie values match. Hi!")
            user = User.get_by_id(int(user_id))
            logging.info("Username is %s" % user.username)
            self.render("welcome.html", username=user.username)
        else:
            logging.info("Some mismatch occurred. Back to signup.")
            self.redirect('/signup')


app = webapp2.WSGIApplication([
	('/', MainHandler),
    ('/signup', SignupHandler),
    ('/welcome', WelcomeHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler)
	], debug=True)



# ERROR CHECKING
class Validate():
    """Class for validation functions"""
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PASS_RE = re.compile(r"^.{3,20}$")
    EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

    def __init__(self, arg):
        super(Validate, self).__init__()
        self.arg = arg

    def username(self):
        pass
        
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def check_errors(params, username, password, verify, email):
    g = User.gql('WHERE username = :1', username).get()
    if not (username and USER_RE.match(username)):
        params['error_username'] = "Missing or invalid username."
    elif g == username:
        params['error_username'] = "Username already exists."
    if not (password and PASS_RE.match(password)):
        params['error_password'] = "Missing or invalid password."
    if password != verify:
        params['error_verify'] = "Passwords don't match."
    if not (email and EMAIL_RE.match(email)):
        params['error_email'] = "There is an error with your email."


# COOKIE HASHING
def hash_cookie(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_cookie(s))

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val

# AUTHENTICATING

def set_login_cookie(self, user):
    '''Sets a cookie that represents a user
    Function receives a User model.'''
    user_id = user.key().id()
    cookie_str = make_secure_val(str(user_id))
    # self.response.headers.add_header('Set-Cookie', 'user=%s' % cookie_str)
    self.response.set_cookie('user', cookie_str)


# PASSWORD HASHING

# Makes a salt
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

# Creates hash from pw
def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    logging.info("%s" % salt)
    h = hashlib.sha256(name+pw+salt).hexdigest()
    logging.info("%s" % h)
    return "%s|%s" % (h, salt)

# Checks if valid pw from hash
def valid_pw(name, pw, h):
    salt = h[h.rfind('|')+1:]
    logging.info("%s" % salt)
    result = make_pw_hash(name, pw, salt) == h
    logging.info("%s" % result)
    return result