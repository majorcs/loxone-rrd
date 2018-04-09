#!/bin/bash

SLOPE="--slope-mode"

rrdtool graph temp_graph_day.png \
	-w 785 -h 400 -a PNG \
	--start -86400 --end now \
	--vertical-label "temperature (°C)" \
	$SLOPE \
	DEF:temp1=temperatures.rrd:temp1:AVERAGE LINE1:temp1#ff0000:"Dolgozó "

rrdtool graph temp_graph_week.png \
	-w 785 -h 400 -a PNG \
	--start -604800 --end now \
	--vertical-label "temperature (°C)" \
	$SLOPE \
	DEF:temp1=temperatures.rrd:temp1:AVERAGE LINE1:temp1#ff0000:"Dolgozó "

