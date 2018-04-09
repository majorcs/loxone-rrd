#!/usr/bin/python

import datetime
import os
import re
import sys
import time

#f = open('/var/log/remote/192.168.88.220/messages', 'r')
#f = open('temp.log', 'r')

for line in sys.stdin:
    print line
    r = re.search('(\d+-\d+-\d+ \d+:\d+:\d+);VI_UP1_1W.01;(.+)$', line.rstrip())
    print r.groups()
    ts = time.mktime(datetime.datetime.strptime(r.group(1), "%Y-%m-%d %H:%M:%S").timetuple())
    os.system("rrdtool update temperatures.rrd {}:{}".format(ts, r.group(2)))
    
