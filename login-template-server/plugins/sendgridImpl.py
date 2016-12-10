from mail import MailSender
from mail import SUCCESS
from mail import SENDER_ADDRESS
from utils import getConfigParam
# import ConfigParser
# import logging

import sendgrid

SENDGRID_API_KEY = getConfigParam('KEYS', 'SENDGRID_API_KEY')

class MailSenderSendGrid(MailSender):
    ''' Sends mails using SendGrid'''

    def send(self, mailto, mailsubject, mailbody):
        return (SUCCESS, "Send mail with SendGrid: " + mailbody)
        outvalue = ""
        sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
        to_email = sendgrid.helpers.mail.Email(mailto)
        from_email = sendgrid.helpers.mail.Email(SENDER_ADDRESS)
        content = sendgrid.helpers.mail.Content('text/plain', mailbody)
        message = sendgrid.helpers.mail.Mail(from_email, mailsubject, to_email, content)
        outvalue = sg.client.mail.send.post(request_body=message.get())
        return (SUCCESS, outvalue)

    def getMaxMailsAllowed(self):
        return 12000

    def getPriority(self):
        return 15 #Lower than DEFAULT_PRIORITY, so it will be attempted before AppEngine
