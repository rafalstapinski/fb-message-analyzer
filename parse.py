from HTMLParser import HTMLParser
import sqlite3
from config import Config
import urllib
import json


class messageParser(HTMLParser):

    newthread = False
    newuser = False
    newmeta = False
    newmessage = False

    thread = None
    person = None
    meta = None
    message = None

    threadperson = None
    sent = None

    threaderror = False

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and len(attrs) > 0:
            if attrs[0][1] == 'thread':
                self.newthread = True
        elif tag == 'span' and len(attrs) > 0:
            if attrs[0][1] == 'user':
                self.newuser = True
            elif attrs[0][1] == 'meta':
                self.newmeta = True
        elif tag == 'p':
            self.newmessage = True

    def handle_endtag(self, tag):
        #print "Encountered an end tag :", tag
        pass

    def handle_data(self, data):
        if self.newthread:
            self.thread = data
            self.newthread = False
            self.getuser(data)

        elif self.newuser:
            self.user = data
            self.newuser = False
            if self.user == self.threadperson:
                self.sent = 'received'
            else:
                self.sent = 'sent'

        elif self.newmeta:
            self.meta = data
            self.newmeta = False

        elif self.newmessage:
            self.message = data
            self.newmessage = False
            print self.thread, self.person, self.meta, self.message

    def getuser(self, uid):

        access_token = urllib.urlencode({'access_token': Config.access_token})
        url = 'https://graph.facebook.com/%s?%s' % (uid, access_token)
        data = json.loads(urllib.urlopen(url).read())


        print data


        self.threadError = True


messages = open('messages.htm')
parser = messageParser()

for line in messages:
    parser.feed(line)
