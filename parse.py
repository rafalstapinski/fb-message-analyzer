from HTMLParser import HTMLParser
import sqlite3
from config import Config
import urllib
import json
import sys
from datetime import datetime
import os
import time

class idParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)

        self.namebook = {}
        self.access_token = Config.access_token
        self.isthread = False

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and len(attrs) > 0:
            if attrs[0][1] == 'thread':
                self.isthread = True

    def handle_data(self, data):
        if self.isthread:
            self.isthread = False
            uid = int(data)

            if uid not in self.namebook:
                token = urllib.urlencode({'access_token': self.access_token})
                url = 'https://graph.facebook.com/%s?%s' % (uid, token)
                graph = json.loads(urllib.urlopen(url).read())

                if 'name' in graph:
                    name = str(graph['name'].encode('utf-8'))
                    self.namebook[uid] = [name]
                    #print uid, self.namebook[uid]

class messageParser(HTMLParser):

    def __init__(self, namebook):
        HTMLParser.__init__(self)
        self.newthread = False
        self.newperson = False
        self.newdate = False
        self.newmessage = False
        self.newme = False

        self.thread = 0
        self.person = None
        self.unix = 0
        self.message = None

        self.sent = 0
        self.threadpeople = []
        self.threadpeoplecount = 0

        self.threaderror = False

        self.conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'messages.db'))
        self.conn.text_factory = str
        self.cur = self.conn.cursor()


        self.namebook = namebook
        self.toinsert = []
        self.me = 0

        # self.cur.execute('''CREATE TABLE `messages` (
	    #                    `id`	INTEGER,
	    #                    `thread`	INTEGER,
	    #                    `person`	TEXT,
	    #                    `sent`	INTEGER,
	    #                    `unix`	INTEGER,
	    #                    `message`	TEXT,
	    #                    `threaderror`	INTEGER,
	    #                    PRIMARY KEY(`id`));''')

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and len(attrs) > 0:
            if attrs[0][1] == 'thread':
                self.newthread = True
                self.threaderror = False
                print self.threadpeople
                self.threadpeople = []
                self.threadpeoplecount = 0
                print len(self.toinsert)
                self.toinsert = []
                # if len(self.toinsert) > 0 and not self.threaderror:
                    # self.cur.executemany('INSERT INTO messages (thread, person, sent, unix, message) VALUES (?, ?, ?, ?, ?)', self.toinsert)
                    # print "inserted ", self.toinsert[0][0]
                #self.toinsert = []
                #self.threaderror = False
        elif tag == 'span' and len(attrs) > 0:
            if attrs[0][1] == 'user':
                self.newperson = True
            elif attrs[0][1] == 'meta':
                self.newdate = True
        elif tag == 'p':
            self.newmessage = True
        elif tag == 'title':
            self.newme = True

    def handle_endtag(self, tag):
        if tag == 'div':
            #self.conn.commit()
            pass
        elif tag == 'body':
            #self.conn.close()
            pass

    def handle_data(self, data):
        # if self.newthread:
        #
        #     self.thread = int(data)
        #     self.newthread = False
        #
        #     access_token = urllib.urlencode({'access_token': Config.access_token})
        #     url = 'https://graph.facebook.com/%s?%s' % (self.thread, access_token)
        #     graph = json.loads(urllib.urlopen(url).read())
        #
        #     if 'name' in graph:
        #         self.threaderror = False
        #
        #         if self.thread not in self.namebook:
        #             self.namebook[self.thread] = [graph['name']]
        #
        #         elif graph['name'] not in self.namebook[self.thread]:
        #             self.namebook[self.thread].append(graph['name'])
        #
        #         print self.namebook[self.thread]
        #
        #     else:
        #         self.threaderror = True
        #         self.thread = None
        #
        # elif self.newperson and not self.threaderror:
        #
        #     self.newperson = False
        #
        #     try:
        #         uid = int(data)
        #         if uid != self.me and uid != self.thread:
        #             self.threaderror = True
        #         elif uid == self.thread:
        #             self.sent = 0
        #         elif uid == self.me:
        #             self.sent = 1
        #         else:
        #             print "wowza this should not be happening"
        #             print self.thread, self.namebook[self.thread]
        #             print self.me, self.namebook[self.me]
        #             sys.exit()
        #     except:
        #         if data not in self.namebook[self.thread] and data not in self.namebook[self.me]:
        #             #print "group msg", data, self.namebook[self.thread], self.namebook[self.me]
        #             #self.threaderror = True
        #             print "group msg", self.thread
        #
        # elif self.newdate and not self.threaderror:
        #     self.newdate = False
        #     print data
        #     self.unix = datetime.strptime(data, '%A, %B %d, %Y at %I:%M%p %Z').strftime('%s')
        #
        # elif self.newmessage and not self.threaderror:
        #     self.newmessage = False
        #     self.message = data
        #
        #     self.toinsert.append((self.thread, self.namebook[self.thread][0], self.sent, self.unix, self.message))

        if self.newthread:
            self.newthread = False

            self.thread = int(data)

            url = 'https://graph.facebook.com/%s?access_token=%s' % (self.thread, Config.access_token)
            graph = json.loads(urllib.urlopen(url).read())

            if 'name' in graph:

                try:
                    name = str(graph['name'].encode('utf-8'))
                except UnicodeEncodeError:
                    print graph
                    sys.exit()

                if self.thread not in self.namebook:
                    self.namebook[self.thread] = [name]

                elif name not in self.namebook[self.thread]:
                    self.namebook[self.thread].append(name)

                print self.namebook[self.thread]

            else:
                self.threaderror = True

        elif self.newperson:
            self.newperson = False

            if not self.threaderror:
                try:
                    self.person = int(data)

                except:
                    name = str(data.encode('utf-8'))

                    if name == self.name:
                        self.person = self.me
                    else:
                        for i in self.namebook:
                            if name in self.namebook[i]:
                                self.person = i
                                break

                if self.person not in self.threadpeople:
                    self.threadpeople.append(self.person)
                    self.threadpeoplecount += 1
                    if self.threadpeoplecount > 2:
                        self.threaderror = True


        elif self.newdate:
            self.newdate = False

            if not self.threaderror:
                self.unix = datetime.strptime(data, '%A, %B %d, %Y at %I:%M%p %Z').strftime('%s')

        elif self.newmessage:
            self.newmessage = False

            if not self.threaderror:
                self.message = data

                self.toinsert.append((self.thread, self.person, self.unix, self.message))

        elif self.newme:
            self.newme = False
            name = str(data[:-11])
            for i in self.namebook:
                if name in self.namebook[i]:
                    self.me = i
                    break

            self.me = 100000196658774
            self.name = "Rafal Stapinski"

messages = open(os.path.join(os.path.dirname(__file__), 'messages.htm'))

idparser = idParser()

# for line in messages:
#     idparser.feed(line)

idparser.namebook = Config.namebook
parser = messageParser(idparser.namebook)

for line in messages:
    parser.feed(line)
