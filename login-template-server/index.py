import os
import logging
import datetime
import webapp2
import json
import time

from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.ndb.key import Key

import utils
from encrypt import Credentials

# Usage:
#
# Add user:   GET http://localhost:14080/apply?username=test4&password=t&alias=test4&icon=user4.png
# Check login:   GET http://localhost:25080/login?username=test1&password=t
# See more examples in html/test.html

DEFAULT_USER = 'anonymous'
SUCCESS = 200
PASSWORD_DEFAULT_LENGTH = 8

class User(ndb.Model):
  """Information about a user.
  """
  username = ndb.StringProperty()
  password = ndb.StructuredProperty(Credentials)
  name = ndb.StringProperty()
  mail = ndb.StringProperty()
  icon = ndb.StringProperty()


class MainPage(webapp2.RequestHandler):

  def get(self):
    html = '<html><head><title>Login template server</title></head>'
    html += '<body><div><h1> <b>LOGIN TEMPLATE SERVER</b></h1></div>'
    html += '<p>This is the server for the <a href="http://login-template.appspot.com">login template</a></p>'
    html += '<p>You may find information about it in the <a href="http://eixerits.wordpress.com">Eixerits blog</a></p>'
    html += '<p>You can test its services in the <a href="./html/test.html">Test page</a></p>'
    html += '</body></html>'
    self.response.write(html)


class LoginHandler(webapp2.RequestHandler):
  """Verifies that a username-password combination is valid.
  Both username and password must be informed in the request.
  """

  def get(self):
    self.post()

  def post(self):
    status = SUCCESS
    json_query_data = ''
    acct = self.request.get('username')
    pw = self.request.get('password')
    if pw == '' or acct == '':
      status = 501
      json_query_data = 'Missing username or password'
    else:
      results = User.query(User.username == acct).fetch(limit=1)
      if len(results) > 0 :
        c = results[0].password
        if not c.verify(pw):
          status = 502
          json_query_data = 'Invalid username or password' # no hints to hackers
        else:
          json_query_data = utils.json_formatter(results)
      else:
        status = 502
        json_query_data = 'Invalid username or password' # no hints to hackers
        time.sleep(3) # hackers can wait...

    utils.write_output(self, json_query_data, status)


class ApplyHandler(webapp2.RequestHandler):
  """Creates a new user account. 
  At least username, password and alias must be informed in the request.
  """

  def get(self):
    self.post()

  def post(self):
    name = self.request.get('alias')
    acct = self.request.get('username')
    mail = self.request.get('mail')
    pw = self.request.get('password')
    icon = self.request.get('icon')
    status = SUCCESS
    json_query_data = ''
    if pw == '' or acct == '' or name == '':
      status = 502
      json_query_data = 'Missing alias, username or password'
    else:
      if utils.exists(User, [['username', acct]]):
        status = 503
        json_query_data = 'Already existing account'
      else:
        # Create the User object and return its key
        newuser = User();
        newuser.name = name
        newuser.username = acct
        newuser.mail = mail
        newuser.icon = icon
        c = Credentials()
        c.set_dk(pw)
        newuser.password = c
        pkey = newuser.put()
        json_query_data = str(pkey.id())
        
    utils.write_output(self, json_query_data, status)


class ChangeProfileHandler(webapp2.RequestHandler):
  """Modifiy information from a user account. 
  The request is assumed to contain all information except password
  So leaving blank any of username, alias, mail or icon will actually 
  store a null value into the missing attribute
  """

  def get(self):
    self.post()

  def post(self):
    name = self.request.get('alias')
    acct = self.request.get('username')
    mail = self.request.get('mail')
    icon = self.request.get('icon')
    json_query_data = ''
    status = SUCCESS
    if acct == '' or name == '':
      json_query_data = 'Missing alias or username'
      status = 504
    else:
      results = User.query(User.username == acct).fetch(limit=1)
      if len(results) == 0 :
        json_query_data = 'Unexisting account'
        status = 505
      else:
        user = results[0];
        user.name = name
        user.mail = mail
        user.icon = icon
        pkey = user.put()
        json_query_data = str(pkey.id());
    utils.write_output(self, json_query_data, status)


class ChangePasswordHandler(webapp2.RequestHandler):
  """Change the password from a user account. 
  Both username and password must be informed in the request.
  """

  def get(self):
    self.post()

  def post(self):
    acct = self.request.get('username')
    pw = self.request.get('password')
    json_query_data = ''
    status = SUCCESS
    if acct == '' or pw == '':
      json_query_data = 'Missing username or password'
      status = 506
    else:
      results = User.query(User.username == acct).fetch(limit=1)
      if len(results) == 0 :
        json_query_data = 'Unexisting account'
        status = 505
      else:
        user = results[0];
        c = Credentials()
        c.set_dk(pw)
        user.password = c
        pkey = user.put()
        json_query_data = str(pkey.id());
    utils.write_output(self, json_query_data, status)


class ResetPasswordHandler(webapp2.RequestHandler):
  """Change the password from a user account. 
  Both username and password must be informed in the request.
  """

  def get(self):
    self.post()

  def post(self):
    acct = self.request.get('username')
#    pw = self.request.get('password')
    json_query_data = ''
    status = SUCCESS
    if acct == '':
      json_query_data = 'Missing username'
      status = 507
    if status == SUCCESS:
      results = User.query(User.username == acct).fetch(limit=1)
      if len(results) == 0 :
        json_query_data = 'Unexisting account'
        status = 505
    if status == SUCCESS:
      user = results[0];
      mailto = user.mail
      if len(mailto) == 0 :
        json_query_data = 'Account without email. Password cannot be reset'
        status = 508
    if status == SUCCESS:
      pw = utils.id_generator(PASSWORD_DEFAULT_LENGTH)
      c = Credentials()
      c.set_dk(pw)
      name = user.name
      user.password = c
      pkey = user.put()
      json_query_data = str(pkey.id())
      with open('html/mail_reset.html', 'r') as myfile:
        subject=myfile.read().replace('\n', '')
      logging.info(subject)
      subject = subject.format(name, acct, pw)
      logging.info(subject)

      (ret, status) = utils.send_email(mailto, "Password reset", subject, True)
      if status != SUCCESS :
        json_query_data = ret
    utils.write_output(self, json_query_data, status)


class SendMailHandler(webapp2.RequestHandler):
  """Send an email. Actually this service is not used directly 
  but we publish it as a convenience for testing purposes
  """

  def get(self):
    self.post()

  def post(self):
    json_query_data = ''
    status = SUCCESS
    mailto = self.request.get('to')
    mailsubject = self.request.get('subject')
    mailbody = self.request.get('body')
    if mailto == '' or mailsubject == '':
      json_query_data = 'Missing adress or subject'
      status = 510
    else:
      (status, json_query_data) = utils.send_email(mailto, mailsubject, mailbody)
    utils.write_output(self, json_query_data, status)


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/login', LoginHandler),
    ('/apply', ApplyHandler),
    ('/changeprofile', ChangeProfileHandler),
    ('/changepassword', ChangePasswordHandler),
    ('/resetpassword', ResetPasswordHandler),
    ('/sendemail', SendMailHandler),
], debug=True)
