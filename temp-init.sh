#!/bin/bash

(zcat /var/log/remote/192.168.88.220/*.gz; cat /var/log/remote/192.168.88.220/messages) |fgrep VI_UP1_1W.01 | ./oldtemp.py

