# -*- coding: utf-8 -*-
'''
post an article to newsmth.net
'''
import urllib, urllib2
import cookielib
import time


def postit(board, title, content):
    if type(title) is unicode:
        title = title.encode('utf-8')
    if type(content) is unicode:
        content = content.encode('utf-8')

    post_data = urllib.urlencode({'subject': title, 'content': content})
    posted = False
    try:
        req = urllib2.Request('http://m.newsmth.net/article/' + board + '/post', post_data)
        urllib2.urlopen(req)
        posted = True
        time.sleep(5)
    except:
        pass
    return posted


def deleteit(board, articleid):
    deleted = False
    try:
        req = urllib2.Request('http://m.newsmth.net/article/' + board + '/delete/' + str(articleid))
        urllib2.urlopen(req)
        deleted = True
        time.sleep(3)
    except:
        pass
    return deleted


def deletearticles(board, tobedeleted):
    deleted = False
    # read the username and password from config file
    f = open('smth.config')
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
    time.sleep(5)

    # post
    posted = True
    for articleid in tobedeleted:
        posted = posted and deleteit(board, articleid)

    # logout
    try:
        req = urllib2.Request('http://m.newsmth.net/user/logout', post_data)
        conn = urllib2.urlopen(req)
        time.sleep(5)
    except:
        pass

    return posted


def postarticle(board, title, link, content):
    posted = False
    # read the username and password from config file
    f = open('smth.config')
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
    time.sleep(5)

    # post
    if type(title) is str:
        title = title.decode('utf-8')
    if type(content) is str:
        content = content.decode('utf-8')
    posted = postit(board, title, title + '\n\n' + link + '\n\n' + content)

    # logout
    try:
        req = urllib2.Request('http://m.newsmth.net/user/logout', post_data)
        conn = urllib2.urlopen(req)
        time.sleep(5)
    except:
        pass

    return posted

