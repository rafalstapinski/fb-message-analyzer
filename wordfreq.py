# wordfreq.py
#     Program to analyze the frequency of words in a text file.
#     Illustrates Python dictionarys

import string

def compareItems((w1,c1), (w2,c2)):
    if c1 > c2:
        return - 1
    elif c1 == c2:
        return cmp(w1, w2)
    else:
        return 1

def count(fname, nwords):

    # get the sequence of words from the file
    text = open(fname,'r').read()
    text = string.lower(text)
    for ch in '!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~':
        text = string.replace(text, ch, ' ')
    words = string.split(text)

    # construct a dictionary of word counts
    counts = {}
    for w in words:
        counts[w] = counts.get(w,0) + 1

    # return analysis of n most frequent words.
    items = counts.items()
    items.sort(compareItems)

    return items[:nwords]
