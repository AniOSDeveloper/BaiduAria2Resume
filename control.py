# coding:utf-8
import socket
import urllib2
import json
import os
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
aria_stop = False
status_file = "/tmp/tv_open"
if os.path.exists(status_file):
    aria_stop = True

host_ip = sys.argv[1]
port = sys.argv[2]


def pause_all():
    aria2_call("aria2.pauseAll")


def resume_all():
    aria2_call("aria2.unpauseAll")


def aria2_call(method):
    jsonreq = json.dumps({'jsonrpc': '2.0', 'id': 'aria2_download', 'method': method, 'params': []})
    response = urllib2.urlopen("http://192.168.0.36:6800/jsonrpc", jsonreq)


try:
    s.connect((host_ip, port))
    if not aria_stop:
        print("pause all")
        pause_all()

    if not os.path.isfile(status_file):
        with open(status_file, 'w') as f:
            f.write("on")

except socket.error as e:
    if aria_stop:
        resume_all()
        print "resume all"
        os.remove(status_file)
finally:
    s.close()
