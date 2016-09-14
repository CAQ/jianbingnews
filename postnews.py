# -*- coding: utf-8 -*-
'''
post a new article (determined by lasttimestamp.txt) from links.txt
by CAQ
May 2013
'''
#from readability.readability import Document
import html2text
from bs4 import BeautifulSoup
import urllib, urllib2, math, re, cookielib
from postsmth import postarticle, deletearticles
#from pymmseg import mmseg

#mmseg.dict_load_defaults()
h2t = html2text.HTML2Text()
h2t.ignore_links = True
h2t.ignore_images = True

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


jobs = {} # multiple jobs: posting in more than one boards a time

# read the latest timestamp we've posted previously
# <board> \t <keyword-1> \t <keyword-2> \t ... \t <keyword-n> \t <last timestamp>
f = open('lasttimestamp.txt')
for line in f:
    board = line[ : line.find('\t')]
    lasttimestamp = int(line[line.rfind('\t') + 1 : ])
    jobs[board] = [line[line.find('\t') + 1 : line.rfind('\t')], lasttimestamp]
f.close()

# now do each job
for board in jobs:
    if board[0] == '#':
        continue

    # Remove old posts with no replies
    tobedeleted = []

    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0'), ('Referer', 'http://m.newsmth.net/'), ('Host', 'm.newsmth.net')]
    urllib2.install_opener(opener)
    req = urllib2.Request('http://m.newsmth.net/board/' + board)
    conn = urllib2.urlopen(req)
    content = conn.read()
    soup = BeautifulSoup(content)
    ul = soup.find('ul', {'class':'list sec'})
    for li in ul.findAll('li'):
      s = str(li)
      if s.find('<a href="/user/query/CAQ9">CAQ9</a>|') <= 0:
          continue
      m = re.search('<a href="/article/' + board + '/([0-9]+)">(.*?)</a>\\(([0-9]+)\\)</div><div>([0-9\\-]+)', s, re.U)
      if m is not None:
          articleid = m.group(1)
          title = m.group(2)
          replies = m.group(3)
          postdate = m.group(4)
          if title.find('[新闻] ') != 0:
              continue
          # A news article
          if replies != '0':
              continue
          # No repiles
          tobedeleted.append(articleid)
    deletearticles(board, tobedeleted)


    lasttimestamp = jobs[board][1]
    jobkeywords = jobs[board][0].strip().split('\t')

    # read the first scan to gather the titles posted
    postedtitles = []
    f = open('links.txt')
    for line in f:
        keyword, link, timestamp, waplink, title, posted = line.strip().split('\t')
        if keyword not in jobkeywords:
            continue
        if posted == '1': # find similar titles against the posted ones
            postedtitles.append(ngram(title, 2))
            # postedtitles.append(wordseg(title))
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
        keyword, link, timestamp, waplink, title, posted = line.strip().split('\t')
        if keyword not in jobkeywords:
            continue
        timestamp = int(timestamp)
        if timestamp <= lasttimestamp:
            continue
        if link.find('www.zzit.com.cn') >= 0: # a spam site
            continue
        titlesegs = ngram(title, 2)
        # titlesegs = wordseg(title)
        repeated = False
        for postedseg in postedtitles:
            c = cossim(postedseg, titlesegs)
            if c > 0.8:
                repeated = True
                break
        if repeated:
            continue
        if mintimestamp == -1 or timestamp < mintimestamp:
            mintimestamp = timestamp
            linkinfo = [link, waplink, title, posted]
    f.close()

    # anything new exists?
    if mintimestamp <= 0:
        continue

    # we've got a new article, post it
    html = urllib.urlopen(linkinfo[1]).read()
    #title = Document(html).short_title() # this short_title isn't always correct
    title = linkinfo[2] # use the title from the search list instead
    #article = Document(html).summary()
    #soup = BeautifulSoup(article)
    #texts = soup.find_all(text=True)
    texts = ''
    texts = h2t.handle(html.decode('utf-8')).split('\n')
    poststr = ''
    for text in texts:
        text = text.strip()
        if len(text) > 0:
            poststr += text + '\n\n'

    if poststr.find(u'搜狗搜索提醒您：') >= 0 and poststr.find(u'该页面可能已被非法篡改，存在安全隐患，请慎重操作！') >= 0:
        poststr = poststr.replace(u'搜狗搜索提醒您：', '')
        poststr = poststr.replace(u'该页面可能已被非法篡改，存在安全隐患，请慎重操作！', '')
        poststr = poststr.replace(u'如需继续访问该页面，请点击下面链接：', '')
        poststr = poststr.replace(u'访问原网页', '请点击链接查看原文哦')
    poststr = poststr.replace(u'搜狗已将原网页转码以便于移动设备浏览', '')
    poststr = poststr.replace(u'返回搜索结果页 \- 搜狗新闻 \- 搜狗首页', '')
    poststr = poststr.replace(u'原网页 \- 意见反馈', '')
    poststr = poststr.replace(u'(点击图片看大图)', u'(原文这里有图片哦)')
    poststr = re.sub(u'\n\\*\\*1.*?尾页\n', '', poststr)

    # remove the bottom part
    #for adsstr in [u'\n## 热门推荐\n', u'\n## 相关搜索\n', u'\n相关阅读\n']:
    for adsstr in [u'\n### 相关新闻\n', u'\n相关推荐\n']:
        adspos = poststr.rfind(adsstr)
        if adspos > 0:
            #print 'Found', adsstr.strip()
            poststr = poststr[0 : adspos]

    if postarticle(board, '[新闻] ' + title, linkinfo[0], poststr):
        # then update the lasttimestamp
        jobs[board][1] = mintimestamp

        # also update link.txt to mark a new "posted"
        fw = open('links.txt', 'w')
        for line in linklines:
            if line.find('\t' + linkinfo[0] + '\t') < 0:
                fw.write(line)
            else:
                fw.write(line[0 : -2] + '1\n')
        fw.close()

# finally, update all the lasttimestamps of the boards
fw = open('lasttimestamp.txt', 'w')
for board in jobs:
    fw.write('\t'.join([board, jobs[board][0], str(jobs[board][1])]) + '\n')
fw.close()

