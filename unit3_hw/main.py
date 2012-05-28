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
import re
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

# HANDLERS
class Handler(webapp2.RequestHandler):
    # function to shorten "response.out.write" to just "write"
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    # function to render (that is, add data to html and compile source file) and return source as a unicode string
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(**params)
    # binds functions above together
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    # Where we query for entries and render the page
    def render_front(self):
        entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC")
        self.render("front.html", entries=entries)

    def get(self):
        self.render_front()

class CreateHandler(Handler):
    #
    def render_create_form(self, subject="", content="", error=""):
        self.render("create.html", subject=subject, content=content, error=error )

    def get(self):
        self.render_create_form()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            # add contents of form to database
            a = Entry(subject=subject, content=content)
            a.put()
            # finds the id of the entity just created to redirect to permalink
            permalink = a.key().id()
            #redirects to permalink
            self.redirect("/%d" % permalink)

class PermalinkHandler(Handler):
    def get(self, permalink):
        link = Entry.get_by_id(permalink)
        if link:
            self.render('entry.html', subject=link.subject, content=link.content)
        else:
            self.render('notfound.html')

# DATABASE
class Entry(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)



app = webapp2.WSGIApplication([
    (r'/', MainHandler),
    (r'/(\d+)', PermalinkHandler),
    (r'/newpost', CreateHandler),
    ], debug=True)
