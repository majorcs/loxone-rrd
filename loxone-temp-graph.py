#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import os
import re
import rrdtool
import sys
import time

rrdtool.create('temperatures.rrd', 
    '--step', '60',
    '-b','now-2d',
    'DS:temp1:GAUGE:86400:-100:100',
    'RRA:AVERAGE:0.5:1m:7d',
    'RRA:AVERAGE:0.5:5m:30d'
    )

for line in sys.stdin:
    r = re.search('(\d+-\d+-\d+ \d+:\d+:\d+);VI_UP1_1W.01;(.+)$', line.rstrip())
    ts = time.mktime(datetime.datetime.strptime(r.group(1), "%Y-%m-%d %H:%M:%S").timetuple())
    print('{}:{}'.format(ts, r.group(2)))
    rrdtool.update('temperatures.rrd', '{}:{}'.format(ts, r.group(2)))

rrdtool.graph('temp_graph_day.png',
	'-w', '785', '-h', '400', '-a', 'PNG',
	'--start', '-86400', '--end', 'now',
	'--vertical-label', 'temperature (°C)',
	'--slope-mode',
	'COMMENT:                  ',
	'COMMENT:Minimum   ',
	'COMMENT:Maximum   ',
	'COMMENT:Average   \l',
	'DEF:temp1=temperatures.rrd:temp1:AVERAGE',
	'LINE1:temp1#ff0000:Dolgozó        ',
	'GPRINT:temp1:MAX:%6.2lf°C  ',
	'GPRINT:temp1:MIN:%6.2lf°C  ',
	'GPRINT:temp1:AVERAGE:%6.2lf°C\l',
	)

rrdtool.graph('temp_graph_week.png',
	'-w', '785', '-h', '400', '-a', 'PNG',
	'--start', '-604800', '--end', 'now',
	'--vertical-label', 'temperature (°C)',
	'--slope-mode',
	'COMMENT:                  ',
	'COMMENT:Minimum   ',
	'COMMENT:Maximum   ',
	'COMMENT:Average   \l',
	'DEF:temp1=temperatures.rrd:temp1:AVERAGE',
	'LINE1:temp1#ff0000:Dolgozó        ',
	'GPRINT:temp1:MAX:%6.2lf°C  ',
	'GPRINT:temp1:MIN:%6.2lf°C  ',
	'GPRINT:temp1:AVERAGE:%6.2lf°C\l',
	)

