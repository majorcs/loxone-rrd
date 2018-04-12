#!/usr/bin/python2
# -*- coding: utf-8 -*-

import codecs
import datetime
import os
import re
import rrdtool
import sys
import time
import yaml

codecs.getreader('utf-8')(sys.stdin)
data = {}
RULE_ORDER=['DEF', 'VDEF', 'CDEF']

def get_params(config):
    ret = []
    if config.has_key('parameters'):
        for p in config['parameters']:
            if config['parameters'][p] != None:
                ret += [p, unicode(config['parameters'][p]).encode('utf-8')]
            else:
                ret += [p]
    if config.has_key('RULES'):
        r = config['RULES'].keys()
        for x in RULE_ORDER:
            try:
                r.remove(x)
            except:
                pass
        r = RULE_ORDER + r
        for n in r:
            if not config['RULES'].has_key(n):
                continue
            print(n)
            for v in config['RULES'][n]:
                param = '{}:{}'.format(n, v.encode('utf-8'))
                ret.append(param)
    
    print ret
    return(ret)
    

pattern = re.compile('(\d+-\d+-\d+ \d+:\d+:\d+);(.*?);([\d.]+)', flags=re.LOCALE)
config = yaml.load(open('graph.conf'))

for line in sys.stdin:
    line = line.strip()
    r = pattern.search(line)
    if r:
        (date, data_name, value) = r.groups()
        data_name = unicode(data_name, 'utf-8')
        ts = time.mktime(datetime.datetime.strptime(r.group(1), "%Y-%m-%d %H:%M:%S").timetuple())
        #print('{}  {}  {}'.format(ts, data_name, value))
        #rrdtool.update('temperatures.rrd', '{}:{}'.format(ts, r.group(2)))
        if data.get(data_name) == None:
            data[data_name] = []
        data[data_name].append({'TS': ts, 'VALUE': value})

#print(config['Data'])
for rrd in data:
    print(rrd)
    if config['Data'].get(rrd) == None:
        print(u"Unknown data key: {}".format(rrd))
        continue

    fname = u'data/{}.rrd'.format(rrd).encode('utf-8')
    p = get_params(config['Data'][rrd])
    rrdtool.create([fname] + p)
    for v in data[rrd]:
        rrdtool.update(fname, '{}:{}'.format(v['TS'], v['VALUE']))

for graph in config['Graphs']:
    if re.match('__', graph):
        continue

    fname = u'data/{}.png'.format(graph).encode('utf-8')
    print(fname)
    p = [fname] + get_params(config['Graphs'][graph])
    print(p)
    rrdtool.graph(p)

#        'COMMENT:                  ',
#        'COMMENT:Minimum   ',
#        'COMMENT:Maximum   ',
#        'COMMENT:Average   \l',
#        'DEF:temp1={}:temp1:AVERAGE'.format(fname),
#        'LINE1:temp1#ff0000:Dolgozó        ',
#        'GPRINT:temp1:MAX:%6.2lf°C  ',
#        'GPRINT:temp1:MIN:%6.2lf°C  ',
#        'GPRINT:temp1:AVERAGE:%6.2lf°C\l',
#        )
