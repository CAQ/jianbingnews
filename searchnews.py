# -*- coding: utf-8 -*-
'''
search news from wap.sogou.com with some keywords
and store the new ones into links.txt
by CAQ
May - Jun 2013
'''
from bs4 import BeautifulSoup
import urllib, urlparse
import time

keywords = ['煎饼', '清华 计算机系']

# read the previous links
# format of the lines: <original link> \t <timestamp> \t <sogou wap link> \t <article title> \t <posted>
links = []
f = open('links.txt')
for line in f:
    link, timestamp, waplink, title, posted = line.strip().split('\t')
    links.append(link)
f.close()

# search the news, typically 10 results
for keyword in keywords:
    base = 'http://wap.sogou.com'
    url = base + '/news/newsSearchResult.jsp?sort=0&keyword=' + urllib.quote(keyword)
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
        title = item.find('a').text
        if type(title) is unicode:
            title = title.encode('utf-8')
        if not link in links:
            fw.write('\t'.join([link, str(timestamp * 1000 + (900 - count)), waplink, title, '0']) + '\n')
        count += 1

    fw.close()

