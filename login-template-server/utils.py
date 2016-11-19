import json
import string
import random
import logging

from google.appengine.api import app_identity
from google.appengine.api import mail

from google.appengine.ext import ndb

""" Utils.
"""

EMAIL_FROM = "eixerit <noreplay@eixerit-test2.appspotmail.com>" #put email sender here. Normally in the format anything@[APP_NAME].appspotmail.com

class Utils():

  def gql_json_parser(self, query_obj):
      ret = []
      for p in query_obj:
        q = p.to_dict(exclude=['password'])
        q['key'] = str(p.key.urlsafe()) #Convert to string to avoid losing precision in Javascript
        ret.append(q)
      return ret

  def obj_format(obj):
      if isinstance(obj, Key):
        if obj.kind() == 'User':
          return obj.id()
        return obj.urlsafe()
      return obj.isoformat() if hasattr(obj, 'isoformat') else obj

  def write_output(self, page, json_query_data, status):
      callback = page.request.get('callback').decode('utf-8').encode('utf-8')
      page.response.headers['Content-Type'] = 'application/json'
      if status:
        json_query_data = [{'status':status, 'result':json_query_data}]
      page.response.out.write('%s(%s)' % (callback, json_query_data))

  def exists(self, model, conditions):
      q = model.query()
      for cond in conditions:
        q = q.filter(ndb.GenericProperty(cond[0]) == cond[1])
        results = q.fetch(limit=1)
      return (len(results) > 0)

  def byteify(self, input):
    if isinstance(input, dict):
        return {self.byteify(key): self.byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [self.byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

  def json_formatter(self, input):
    return self.byteify(json.loads(json.dumps(self.gql_json_parser(input), default=self.obj_format)))

  def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

  def send_email(self, mailto, mailsubject, mailbody):
    outvalue = ""
#    message = mail.EmailMessage()
    sender_address = (
        'noreply@{}.appspotmail.com'.format(
            app_identity.get_application_id()))
    message = mail.EmailMessage(
        sender = sender_address,
        subject = mailsubject)

    message.to = mailto
    message.body = mailbody

#       '{}@appspot.gserviceaccount.com'.format(
#            app_identity.get_application_id()))
#    sender_address = (
#        'your_alias <{}@appspot.gserviceaccount.com>'.format(
#            app_identity.get_application_id()))
#    message.sender = EMAIL_FROM

#    message.sender = sender_address
    if not mail.is_email_valid(mailto):
      outvalue = "Email Address for TO Address is Invalid"
    if outvalue == "":
      message.to = mailto
      if len(mailbody) == 0 or len(mailsubject) > 0:
        outvalue = "Subject or Body was left Empty"
    if outvalue == "":
#        message.subject = mailsubject
        message.body = mailbody
    try:
      logging.info("************** sending....")
      message.send()
      logging.info("************** sent")
    except Exception, message:
      logging.info(message)
      #outvalue = str(message)
      outvalue = "wowo error"