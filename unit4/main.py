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

class Handler(webapp2.RequestHandler):
    # function that simplifies sending requests:
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    # function that renders string of template:
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render()
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
        self.render("signup.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')


        errors = {}
        check_errors(errors, username, password, verify, email)
        if len(errors) == 0:
            pass
        else:
            errors['username'] = username
            errors['email'] = email
            self.render("signup.html", **errors)

        

app = webapp2.WSGIApplication([
	('/', MainHandler),
    ('/signup', SignupHandler),
	], debug=True)




USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

def valid_username(username):
    return username and USER_RE.match(username)

def valid_password(password):
    return password and PASS_RE.match(password)

def valid_email(email):
    return not email or EMAIL_RE.match(email)

def check_errors(params, username, password, verify, email):
    if not valid_username(username):
        params['username_error'] = "Missing or invalid username."
    if not valid_password(password):
        params['password_error'] = "Missing or invalid password."
    if password != verify:
        params['verify_error'] = "Passwords don't match."
    if not valid_email(email):
        params['email_error'] = "There is an error with your email."

