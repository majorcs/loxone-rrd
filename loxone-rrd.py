#!/usr/bin/python2
# -*- coding: utf-8 -*-

import codecs
import datetime
import getopt
import os
import re
import rrdtool
import signal
import sys
import syslog
import threading
import time
import yaml

reload(sys)  
sys.setdefaultencoding('utf8')

codecs.getreader('utf-8')(sys.stdin)
data = {}
RULE_ORDER=['DEF', 'VDEF', 'CDEF']
EOF=False
syslog.openlog('loxone-rrd', syslog.LOG_PID | syslog.LOG_USER )


def log(msg):
    if sys.stdout.isatty():
        print(unicode(msg).encode('utf-8'))
    else:
        syslog.syslog(unicode(msg).encode('utf-8'))


def generate_graph(interval, config):
    while not EOF:
        for i in xrange(interval):
            if EOF:
                break
            time.sleep(1)

        log("Generating graphs {}".format(EOF))
        rrd_graph(config)
        log("Graph generation done")

    log("Exiting from graph thread")

    
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


def rrd_graph(config):
    graphdir = config.get('Parameters', {}).get('graphdir', '/var/www/loxone-rrd')
    for graph in config['Graphs']:
        if re.match('__', graph):
            continue

        fname = u'{}/{}.png'.format(graphdir, graph).encode('utf-8')
        p = [fname] + get_params(config['Graphs'][graph])
        p += ['COMMENT:\\n', 'COMMENT:Last update\\: {}\\r'.format(time.strftime('%Y-%m-%d %H\\:%M\\:%S'))]
        print(p)
        log("Generating: {}".format(fname))
        try:
            rrdtool.graph(p)
        except Exception as e:
            log("Error: {}".format(e))
    

pattern = re.compile('(\d+-\d+-\d+ \d+:\d+:\d+);(.*?);([\d.]+)', flags=re.LOCALE)
log(u'Starting up')

opts, args = getopt.getopt(sys.argv[1:], 'c:', ['config='])
config = '/etc/loxone-rrd.conf'

for o, a in opts:
    if o in ('-c', '--config'):
        config = a

log('Opening config: {}'.format(config))
try:
    config = yaml.load(open(config))
except Exception as e:
    log("Error opening config: {}".format(e))
    time.sleep(1)
    exit(1)

if config.get('Parameters').has_key('workdir'):
    d = config['Parameters']['workdir']
    log("Changing working dir to: {}".format(d))
    os.chdir(d)

graph_interval = int(config.get('Parameters', {}).get('graph_interval', 120))
log("Setting up graph generation interval: {}".format(graph_interval))
t = threading.Thread(target=generate_graph, kwargs={'interval': graph_interval, 'config': config})
t.start()

while not EOF:
    try:
        line = sys.stdin.readline()
    except (BaseException, Exception) as e:
        log("Error during read: {}".format(e))
        EOF = True
        break

    if line == '':
        EOF = True
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
t.join()
