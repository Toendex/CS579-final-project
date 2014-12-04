import ConfigParser
import sys
import time

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

twitter = get_twitter('twitter.cfg')
print 'Established Twitter connection.'

import time
from datetime import datetime
print datetime.utcnow()

import time
from datetime import datetime
import cPickle
import os.path
import random
outfiles=[]
tweetnums=[]
path=‘stream_data/'
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
i=0
while True:
    try:
        for r in twitter.request('statuses/sample',{'language':'en'}):
            if not 'user' in r:
                continue
            tn=datetime.utcnow().timetuple()
            while 'retweeted_status' in r:
                r=r['retweeted_status']
            t=r['created_at']
            ts=time.strptime(t,'%a %b %d %H:%M:%S +0000 %Y')
            tdis=time.mktime(tn)-time.mktime(ts)
            if tdis<600 and r['retweet_count']==0:
                continue
            dic={'tweet':r, 'create_struct_time':ts, 'now_struct_time':tn, 'time_difference_in_second':tdis}
            cPickle.dump(dic, outfiles[ts.tm_hour])
            tweetnums[ts.tm_hour]=tweetnums[ts.tm_hour]+1
            if tweetnums[ts.tm_hour]==10:
                outfiles[ts.tm_hour].flush()
                tweetnums[ts.tm_hour]=0
            print r['created_at'],' : ', r['retweet_count'], ':', tdis
            i+=1
            if i%100==0:
                print i,' tweets'
    except:
        print "Unexpected error:", sys.exc_info()[0]
