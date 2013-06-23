# -*- coding: utf-8 -*-
'''
post a new article (determined by lasttimestamp.txt) from links.txt
by CAQ
May 2013
'''
from readability.readability import Document
from bs4 import BeautifulSoup
import urllib, math, re
from postsmth import postarticle
from pymmseg import mmseg

mmseg.dict_load_defaults()

# word segmentation using mmseg
def wordseg(text):
    words = {}
    algor = mmseg.Algorithm(text)
    for tok in algor:
        if tok.text not in words:
            words[tok.text] = 0
        words[tok.text] += 1
    return words

# generate n-grams
def ngram(text, n):
    if type(text) is str:
        text = text.decode('utf-8')
    ngrams = {}
    for segment in re.split(u'([\u3400-\u4dbf\u4e00-\u9fff]+)', text.lower()):
        segment = segment.strip()
        if len(segment) <= 0:
            continue
        if re.match(u'[\u3400-\u4dbf\u4e00-\u9fff]+', segment) is not None:
            # chinese
            for i in range(0, len(segment) - n + 1):
                ngram = segment[i : i + n]
                if ngram not in ngrams:
                    ngrams[ngram] = 0
                ngrams[ngram] += 1
        else:
            if segment not in ngrams:
                ngrams[segment] = 0
            ngrams[segment] += 1
    return ngrams

# cosine similarity
def cossim(d1, d2):
    s0 = 0
    s1 = 0
    s2 = 0
    for k in d1:
        s1 += d1[k] * d1[k]
        if k in d2:
            s0 += d1[k] * d2[k]
    for k in d2:
        s2 += d2[k] * d2[k]
    return s0 / math.sqrt(s1) / math.sqrt(s2)

# read the latest timestamp we've posted previously
f = open('lasttimestamp.txt')
lasttimestamp = int(f.readline())
f.close()

# read the first scan to gather the titles posted
postedtitles = []
f = open('links.txt')
for line in f:
    link, timestamp, waplink, title, posted = line.strip().split('\t')
    if posted == '1': # find similar titles against the posted ones
        # postedtitles.append(ngram(title, 2))
        postedtitles.append(wordseg(title))
f.close()

# read all the links, find the minimum one that 
# hasn't been posted (greater than lasttimestamp), nor repeated.
# meanwhile, store all the links for output later
linklines = []
mintimestamp = -1
linkinfo = []
f = open('links.txt')
for line in f:
    linklines.append(line)
    link, timestamp, waplink, title, posted = line.strip().split('\t')
    timestamp = int(timestamp)
    if timestamp <= lasttimestamp:
        continue
    if link.find('www.zzit.com.cn') >= 0:
        continue
    # titlesegs = ngram(title, 2)
    titlesegs = wordseg(title)
    repeated = False
    for postedseg in postedtitles:
        c = cossim(postedseg, titlesegs)
        if c > 0.5:
            repeated = True
            break
    if repeated:
        continue
    if mintimestamp == -1 or timestamp < mintimestamp:
        mintimestamp = timestamp
        linkinfo = [link, waplink, title, posted]
f.close()

# anything new exists?
if mintimestamp > 0:
    # we've got a new article, post it
    html = urllib.urlopen(linkinfo[1]).read()
    #title = Document(html).short_title() # this short_title isn't always correct
    title = linkinfo[2] # use the title from the search list instead
    article = Document(html).summary()
    soup = BeautifulSoup(article)
    texts = soup.find_all(text=True)
    poststr = ''
    for text in texts:
        text = text.strip()
        if len(text) > 0:
            poststr += text + '\n\n'
    postarticle(title, linkinfo[0], poststr)

    # then update the lasttimestamp
    fw = open('lasttimestamp.txt', 'w')
    fw.write(str(mintimestamp))
    fw.close()

    # also update link.txt to mark a new "posted"
    fw = open('links.txt', 'w')
    for line in linklines:
        if line.find(linkinfo[0] + '\t') != 0:
            fw.write(line)
        else:
            fw.write(line[0 : -2] + '1\n')
    fw.close()
