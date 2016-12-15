import json
import string
import random

import logging

""" Utils.
"""

SUCCESS = 200

def getConfigParam(section, param):
  import ConfigParser
  config = ConfigParser.RawConfigParser()
  config.read('config.ini')
  return config.get(section, param)

def byteify(input):
  if isinstance(input, dict):
      return {byteify(key): byteify(value)
              for key, value in input.iteritems()}
  elif isinstance(input, list):
      return [byteify(element) for element in input]
  elif isinstance(input, unicode):
      return input.encode('utf-8')
  else:
      return input

def gql_json_parser(query_obj):
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

def json_formatter(input):
  return byteify(json.loads(json.dumps(gql_json_parser(input), default=obj_format)))

def exists(model, conditions):
  q = model.query()
  for cond in conditions:
    q = q.filter(ndb.GenericProperty(cond[0]) == cond[1])
    results = q.fetch(limit=1)
  return (len(results) > 0)

def write_output(page, json_query_data, status):
  callback = page.request.get('callback').decode('utf-8').encode('utf-8')
  page.response.headers['Content-Type'] = 'application/json'
  if status:
    json_query_data = [{'status':status, 'result':json_query_data}]
  page.response.out.write('%s(%s)' % (callback, json_query_data))

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for _ in range(size))

def send_email(mailto, mailsubject, mailbody, ishtml=False):
  from mail import MailSender
  (status, outvalue) = MailSender().checkValidEmail(mailto, mailsubject, mailbody)
  if (status != SUCCESS):
    return (status, outvalue)
  sender_list = MailSender().getImplementations()
  for sender in sender_list:
    if (sender.hasAvailableQuota()):
      (status, outvalue) = sender.send(mailto, mailsubject, mailbody, ishtml)
      if (status == SUCCESS):
        sender.incrementNumMailsSent()
        return (status, outvalue)

  return (512, "No sender was able to send the email")
