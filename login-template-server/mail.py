from google.appengine.api import app_identity
from google.appengine.api import mail
import datetime
from google.appengine.ext import ndb
from plugins import PluginHandler

""" Sending mail classes.
"""

SUCCESS = 200
DEFAULT_QUOTA_LIMIT = 999999 # By default very high limit
DEFAULT_PRORITY = 10 # By default medium priority (allows easy assignment of higher or lower vaues to new classes)
SENDER_ALIAS = 'your_alias' #put an alias to use in sent emails. By default in the format alias <noreply@[APP_NAME].appspotmail.com>
SENDER_ADDRESS = SENDER_ALIAS + ' <noreply@{}.appspotmail.com>'.format(app_identity.get_application_id())

class MailStats(ndb.Model):
  """Emails sent registry.
  """
  senderType = ndb.StringProperty()
  period = ndb.DateTimeProperty() #auto_now_add=True)
#  dateSent = ndb.DateTimeProperty(auto_now_add=True)
  numMails = ndb.IntegerProperty(indexed=False)


class MailSender(object):
    """ Interface / Abstract Class, so it cannot be called directly.
        Implements a default behaviour for each method except for the 'send' 
        which must be explicitly implemented in each subclass"""

    def send(self, mailto, mailsubject, mailbody):
        raise NotImplementedError('Abstract method send cannot be called directly')

    def getCurrentPeriod(self):
        return datetime.datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def getNumMailsSent(self):
        senderType = self.__class__.__name__
        currentMonth = self.getCurrentPeriod()
        q = MailStats.query(MailStats.senderType == senderType, MailStats.period == currentMonth)
        try:
            value = q.fetch()[0].numMails
        except IndexError as e:
            return 0
        return value

    def incrementNumMailsSent(self):
        senderType = self.__class__.__name__
        currentMonth = self.getCurrentPeriod()
        q = MailStats.query(MailStats.senderType == senderType, MailStats.period == currentMonth)
        try:
            stats = q.fetch()[0]
            stats.numMails = stats.numMails + 1
        except IndexError as e: #First mail in the period
            stats = MailStats()
            stats.senderType = senderType
            stats.period = currentMonth
            stats.numMails = 1
        stats.put()

    def getMaxMailsAllowed(self):
        return DEFAULT_QUOTA_LIMIT 

    def hasAvailableQuota(self):
        return self.getNumMailsSent() < self.getMaxMailsAllowed()

    def getPriority(self):
        return DEFAULT_PRORITY

    @staticmethod
    def checkValidEmail(mailto, mailsubject, mailbody):
        status = SUCCESS
        outvalue = ""
        if len(mailbody) == 0 or len(mailsubject) == 0:
            status = 511
            outvalue = "Subject or Body was left Empty"
        elif not mail.is_email_valid(mailto):
            status = 512
            outvalue = "Email Address for TO Address is Invalid"
        return (status, outvalue)

    @staticmethod
    def getImplementations():
        PluginHandler.load()
        return sorted([cls() for cls in MailSender.__subclasses__()], key=lambda x: x.getPriority())


class MailSenderAppEngine(MailSender):
    ''' Sends mails using AppEngine. This implementation is always available'''

    def send(self, mailto, mailsubject, mailbody):
        return (SUCCESS, "Send mail with AppEngine: " + mailbody)
        sender_address = SENDER_ADDRESS
        message = mail.EmailMessage(
          sender = sender_address,
          subject = mailsubject)
        message.to = mailto
        message.body = mailbody
        message.send()
        return (SUCCESS, "Send mail with AppEngine: " + mailbody)
