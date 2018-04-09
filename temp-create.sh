#!/bin/bash

rrdtool create temperatures.rrd \
	--step 60 \
	-b now-2d \
	DS:temp1:GAUGE:86400:-100:100 \
	RRA:AVERAGE:0.5:1m:7d \
	RRA:AVERAGE:0.5:5m:30d
