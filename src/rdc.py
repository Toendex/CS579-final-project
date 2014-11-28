import ConfigParser
import sys
import time
from datetime import datetime
import cPickle
import os.path
import random

import matplotlib.pyplot as plt
import networkx as nx
from TwitterAPI import TwitterAPI

# This method is done for you.
def get_twitter(config_file):
    """ Read the config_file and construct an instance of TwitterAPI.
    Args:
      config_file ... A config file in ConfigParser format with Twitter credentials
    Returns:
      An instance of TwitterAPI.
    """
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    twitter = TwitterAPI(
                   config.get('twitter', 'consumer_key'),
                   config.get('twitter', 'consumer_secret'),
                   config.get('twitter', 'access_token'),
                   config.get('twitter', 'access_token_secret'))
    return twitter


def readUFromFile(userfilepath):
    ifCheckNextTweet=False
    uids=[]
    users=[]
    if not os.path.exists(userfilepath):
        return uids,users
    userfile=open(userfilepath,'rb')
    while True:
        try:
            if ifCheckNextTweet:
                ifCheckNextTweet=False
            u=cPickle.load(userfile)
            uids.append(u['id'])
            users.append(u)
        except EOFError:
            break
        except:
            print "Unexpected error:", sys.exc_info()[0]
            ifCheckNextTweet=True
            continue
    userfile.close()
    return uids,users
    
def getU(twitter,maxUserNum):
    i=0
    u=0
    users=[]
    while True:
        try:
            for r in twitter.request('statuses/sample',{'language':'en'}):
                if not 'user' in r:
                    continue
                if i%30!=0:
                    continue
                users.append(r['user'])
#                 while 'retweeted_status' in r:
#                     r=r['retweeted_status']
#                     if 'retweeted_status' in r:
#                         continue
#                     users.append(r['user'])
                u+=1
                if u>=maxUserNum:
                    return users
        except:
            print "Unexpected error:", sys.exc_info()[0]
            
def robust_request(twitter, resource, params, max_tries=5):
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print >> sys.stderr, 'Got error:', request.text, '\nsleeping for 15 minutes.'
            sys.stderr.flush()
            time.sleep(60 * 15)
            
def readUserTimeLine(twitter,newu,usersfile,outfiles,tweetnums,maxReadNum=600,maxPageNum=10,maxTime=11289600,lang='en'):
    tdiff=0
    max_id=-1
    readNum=0
    pageNum=0
    cPickle.dump(newu, usersfile)
    usersfile.flush()
    while True:
        tn=datetime.utcnow().timetuple()
        rs=[]
        if max_id==-1:
            rs=robust_request(twitter,'statuses/user_timeline',{'user_id':newu['id'],'count':200})
        else:
            rs=robust_request(twitter,'statuses/user_timeline',{'user_id':newu['id'],'count':200,'max_id':max_id})
        n=0
        for r in rs:
            n+=1
            max_id=r['id']-1
            if 'retweeted_status' in r:
                continue
            if not 'lang' in r:
                continue
            if r['lang']!=lang:
                continue
            t=r['created_at']
            ts=time.strptime(t,'%a %b %d %H:%M:%S +0000 %Y')
            tdis=time.mktime(tn)-time.mktime(ts)
            dic={'tweet':r, 'create_struct_time':ts, 'now_struct_time':tn, 'time_difference_in_second':tdis}
            cPickle.dump(dic, outfiles[ts.tm_hour])
            tweetnums[ts.tm_hour]=tweetnums[ts.tm_hour]+1
            if tweetnums[ts.tm_hour]==10:
                outfiles[ts.tm_hour].flush()
                tweetnums[ts.tm_hour]=0
            if tdiff<tdis:
                tdiff=tdis
            readNum+=1
            if readNum>=maxReadNum:
                return readNum
        pageNum+=1
        if n!=200 or pageNum>=maxPageNum or tdiff>=maxTime: #two weeks
            break
    return readNum

twitter = get_twitter('weodne.cfg')
print 'Established Twitter connection.'
outfiles=[]
tweetnums=[]
path='rest_data/'
if not os.path.exists(path):
    os.makedirs(path)
for i in range(0,24):
    si=str(i)
    if os.path.exists(path+si):
        outfile=open(path+si,'ab')
    else:
        outfile=open(path+si,'wb')
    outfiles.append(outfile)
    tweetnums.append(0)
    
usersfilename='users'
usersfile=1
uids,users=readUFromFile(path+usersfilename)
print 'read',len(uids),'uids from user_file'
print 'read',len(users),'users from user_file'
if os.path.exists(path+usersfilename):
    usersfile=open(path+usersfilename,'ab')
else:
    usersfile=open(path+usersfilename,'wb')
    
totalreadnum=0
rs=robust_request(twitter,'statuses/home_timeline',{'count':200})
newauthus=[]
for r in rs:
    if r['user']['id'] in uids:
        continue
    uids.append(r['user']['id'])
    users.append(r['user'])
    newauthus.append(r['user'])
for u in newauthus:
    readnum=readUserTimeLine(twitter,u,usersfile,outfiles,tweetnums,maxReadNum=1000)
    totalreadnum+=readnum
    print 'readnum:',readnum,'\ttotalreadnum:',totalreadnum

while True:
    us=getU(twitter,360);
    newus=[]
    for u in us:
        if u['id'] in uids:
            continue
        uids.append(u['id'])
        users.append(u)
        newus.append(u)
    for newu in newus:
        readnum=readUserTimeLine(twitter,newu,usersfile,outfiles,tweetnums)
        totalreadnum+=readnum
        print 'readnum:',readnum,'\ttotalreadnum:',totalreadnum
    