from threading import Thread
from twilio.rest import TwilioRestClient
from twilio_creds import ACCOUNT, TOKEN
import time
import datetime
from email.utils import parsedate_tz

TWILIO_MSG_DURATION = 4

client = TwilioRestClient(ACCOUNT, TOKEN)

class MessagePoll(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.messages = []
        self.last_msg_at = datetime.datetime.utcnow()

    def run(self):
        while True:
            msgs = [msg for msg in client.sms.messages.list(to="5038226827")]
            msgs = [msg for msg in msgs if parsedate_tz(msg.date_created)
                                           > self.last_msg_at.timetuple()]
            self.messages.extend([msg.body.replace('\n',' ') for msg in msgs])
            if self.messages:
                self.last_msg_at = datetime.datetime.utcnow()
            #self.messages.append('foobarbazqaaa'*14)
            time.sleep(TWILIO_MSG_DURATION + 2)



#def get_messages():
    #for message in client.sms.messages.list():
        #yield message.body

