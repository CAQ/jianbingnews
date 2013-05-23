# -*- coding: utf-8 -*-
'''
post an article to newsmth.net
'''
import urllib, urllib2
import cookielib
#import time

def postit(title, content):
    if type(title) is unicode:
        title = title.encode('utf-8')
    if type(content) is unicode:
        content = content.encode('utf-8')

    post_data = urllib.urlencode({'subject': title, 'content': content})
    req = urllib2.Request('http://m.newsmth.net/article/DCST.THU/post', post_data)
    urllib2.urlopen(req)
    #time.sleep(30)

def postarticle(title, link, content):
    # read the username and password from config file
    f = open('smthdcst.config')
    usr, pwd = f.readline().strip().split('\t')
    f.close()

    # login
    post_data = urllib.urlencode({'id': usr, 'passwd': pwd})
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0'), ('Referer', 'http://m.newsmth.net/'), ('Host', 'm.newsmth.net')]
    urllib2.install_opener(opener)
    req = urllib2.Request('http://m.newsmth.net/user/login', post_data)
    conn = urllib2.urlopen(req)

    # post
    postit(title, link + '\n\n' + content)

    # logout
    req = urllib2.Request('http://m.newsmth.net/user/logout', post_data)
    conn = urllib2.urlopen(req)

