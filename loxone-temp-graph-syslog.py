#!/usr/bin/python2
# -*- coding: utf-8 -*-

import codecs
import datetime
import os
import re
import rrdtool
import sys
import syslog
import time
import yaml

reload(sys)  
sys.setdefaultencoding('utf8')

codecs.getreader('utf-8')(sys.stdin)
data = {}
RULE_ORDER=['DEF', 'VDEF', 'CDEF']
syslog.openlog('loxone-rrd', syslog.LOG_PID | syslog.LOG_USER )

def log(msg):
    syslog.syslog(unicode(msg).encode('utf-8'))

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
            for v in config['RULES'][n]:
                param = '{}:{}'.format(n, v.encode('utf-8'))
                ret.append(param)
    
    return(ret)

def generate_graph(config):
    for graph in config['Graphs']:
        if re.match('__', graph):
            continue

        fname = u'{}.png'.format(graph).encode('utf-8')
        p = [fname] + get_params(config['Graphs'][graph])
        rrdtool.graph(p)
    

pattern = re.compile('(\d+-\d+-\d+ \d+:\d+:\d+);(.*?);([\d.]+)', flags=re.LOCALE)
config = yaml.load(open('graph.conf'))

log(u'Starting up')
if config.get('Parameters').has_key('workdir'):
    d = config['Parameters']['workdir']
    log("Changing working dir to: {}".format(d))
    os.chdir(d)
    

EOF=False
while not EOF:
    line = sys.stdin.readline()
    if line == '':
        break
    line = line.strip()
    r = pattern.search(line)
    if not r:
        continue
        
    (date, data_name, value) = r.groups()
    data_name = unicode(data_name, 'utf-8')
    ts = time.mktime(datetime.datetime.strptime(r.group(1), "%Y-%m-%d %H:%M:%S").timetuple())

    if not config['Data'].get(data_name):
        log("Unknown data key: {}".format(data_name))
        continue

    fname = u'{}.rrd'.format(data_name).encode('utf-8')
    if not os.path.isfile(fname):
        log("Create new RRD database: {}".format(data_name))
        p = get_params(config['Data'][data_name])
        try:
            rrdtool.create([fname] + p)
        except Exception as e:
            log("Error creating RRD: {}".format(e))

    try:
        rrdtool.update(fname, '{}:{}'.format(ts, value))
    except Exception as e:
        log("Error updating RRD: {}".format(e))

log("Exiting")
