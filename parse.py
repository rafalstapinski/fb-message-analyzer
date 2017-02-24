from HTMLParser import HTMLParser
import sqlite3
from config import Config
import urllib
import json
import sys
from datetime import datetime
import os

class messageParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.newthread = False
        self.newperson = False
        self.newdate = False
        self.newmessage = False

        self.thread = 0
        self.person = None
        self.date = None
        self.message = None

        self.threadperson = None
        self.threadpeople = []
        self.sent = 0

        self.threaderror = False

        #self.conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'messages1.db'))
        #self.conn.text_factory = str
        #self.cur = self.conn.cursor()

        self.sentTo = 0
        self.receivedFrom = 0

        self.namebook = {}
        self.peopleyouvetalkedto = []

        # self.cur.execute('''CREATE TABLE `messages` (
	    #                    `id`	INTEGER,
	    #                    `thread`	INTEGER,
	    #                    `threadperson`	TEXT,
	    #                    `sent`	INTEGER,
	    #                    `ts`	TEXT,
	    #                    `message`	TEXT,
	    #                    `threaderror`	INTEGER,
	    #                    PRIMARY KEY(`id`));''')

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and len(attrs) > 0:
            if attrs[0][1] == 'thread':
                self.newthread = True
        elif tag == 'span' and len(attrs) > 0:
            if attrs[0][1] == 'user':
                self.newperson = True
            elif attrs[0][1] == 'meta':
                self.newdate = True
        elif tag == 'p':
            self.newmessage = True

    def handle_endtag(self, tag):
        if tag == 'div':
            #self.conn.commit()
            pass
        elif tag == 'body':
            #self.conn.close()
            pass

    def handle_data(self, data):
        if self.newthread:
            self.thread = int(data)
            self.newthread = False

            access_token = urllib.urlencode({'access_token': Config.access_token})
            url = 'https://graph.facebook.com/%s?%s' % (self.thread, access_token)
            graph = json.loads(urllib.urlopen(url).read())

            if 'name' in graph:
                self.threadperson = graph['name']
                self.threaderror = False

                if self.thread not in self.namebook:
                    self.namebook[self.thread] = [self.threadperson]
                #print 'new thread with ', self.threadperson
            else:
                self.threadperson = None
                self.threaderror = True
                #print 'new error with ', self.thread

            self.sentTo = 0
            self.receivedFrom = 0

            #print self.peopleyouvetalkedto

            print data


        elif self.newperson:

            try:
                int(data)
                if int(data) in self.namebook:
                    self.person = self.namebook[int(data)]
                else:
                    access_token = urllib.urlencode({'access_token': Config.access_token})
                    url = 'https://graph.facebook.com/%s?%s' % (self.thread, access_token)
                    graph = json.loads(urllib.urlopen(url).read())

                    if 'name' in graph:
                        self.person =

            except:
                self.person = data

            if self.person not in self.peopleyouvetalkedto:
                self.peopleyouvetalkedto.append(self.person)

            self.newperson = False
            if self.person == self.threadperson:
                self.sent = 0
            else:
                self.sent = 1

        elif self.newdate:
            self.date = datetime.strptime(data[:-4], '%A, %B %d, %Y at %I:%M%p')
            self.newdate = False

        elif self.newmessage:
            self.message = data
            self.newmessage = False

            if self.sent == 0:
                self.receivedFrom += 1
            elif self.sent == 1:
                self.sentTo += 1

            #print self.threadperson, self.person, self.sent, self.sentTo, self.receivedFrom

            # self.cur.execute('INSERT INTO messages (thread, threadperson, sent, ts, message, threaderror) VALUES (?, ?, ?, ?, ?, ?)', (self.thread, self.threadperson, self.sent, self.date, self.message, self.threaderror))

messages = open(os.path.join(os.path.dirname(__file__), 'messages.htm'))
parser = messageParser()

for line in messages:
    parser.feed(unicode(line))
