# -*- coding: utf-8 -*-
'''
search news from wap.sogou.com with the keyword 煎饼
and store the new ones into links.txt
by CAQ
May 2013
'''
from bs4 import BeautifulSoup
import urllib, urlparse
import time

# read the previous links
# format of the lines: <link> \t <timestamp>
links = []
f = open('links.txt')
for line in f:
    link, timestamp, waplink = line.strip().split('\t')
    links.append(link)
f.close()

# search the news, typically 10 results
base = 'http://wap.sogou.com'
url = base + '/news/newsSearchResult.jsp?sort=0&keyword=%E7%85%8E%E9%A5%BC'
soup = BeautifulSoup(urllib.urlopen(url).read())
timestamp = int(time.time())
count = 0

# if the news is new, store it
fw = open('links.txt', 'a')

for item in soup.find_all('div', class_='list-item'):
    waplink = base + item.find('a').get('href')
    querystr = urlparse.urlparse(waplink).query
    query = urlparse.parse_qs(querystr)
    link = query['url'][0]
    if not link in links:
        fw.write('\t'.join([link, str(timestamp * 1000 + (900 - count)), waplink]) + '\n')
    count += 1

fw.close()

