# -*- coding: utf-8 -*-
'''
post a new article (determined by lasttimestamp.txt) from links.txt
by CAQ
May 2013
'''
from readability.readability import Document
from bs4 import BeautifulSoup
import urllib
from postsmth import postarticle

# read the latest timestamp we've posted previously
f = open('lasttimestamp.txt')
lasttimestamp = int(f.readline())
f.close()

# read all the links, find the minimum one that 
# hasn't been posted (greater than lasttimestamp)
mintimestamp = -1
linkinfo = [] # [link, waplink, title]
f = open('links.txt')
for line in f:
    link, timestamp, waplink, title = line.strip().split('\t')
    timestamp = int(timestamp)
    if timestamp <= lasttimestamp:
        continue
    if mintimestamp == -1 or timestamp < mintimestamp:
        mintimestamp = timestamp
        linkinfo = [link, waplink, title]
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
    if len(poststr) > 0:
        if title.find('杨光') < 0 and title.find('女童') < 0:
            postarticle(title, linkinfo[0], poststr)

    # then update the lasttimestamp
    fw = open('lasttimestamp.txt', 'w')
    fw.write(str(mintimestamp))
    fw.close()

