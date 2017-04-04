import os
import parse
import wordfreq

messages = open(os.path.join(os.path.dirname(__file__), 'messages.htm'))

idparser = parse.idParser()

for line in messages:
    idparser.feed(line)

print idparser.me

# parser = parse.messageParser(idparser.namebook)
#
# messages = open(os.path.join(os.path.dirname(__file__), 'messages.htm'))
#
# for line in messages:
#     parser.feed(line)
