# coding:utf-8
import socket
import urllib2
import json
import os
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tv_open = False
status_file = "/tmp/tv_open"
if os.path.exists(status_file):
    tv_open = True

host_ip = sys.argv[1]
if not host_ip:
    sys.exit(0)


def pause_all():
    aria2_call("aria2.pauseAll")


def resume_all():
    aria2_call("aria2.unpauseAll")


def aria2_call(method):
    jsonreq = json.dumps({'jsonrpc': '2.0', 'id': 'aria2_download', 'method': method, 'params': []})
    response = urllib2.urlopen("http://192.168.0.36:6800/jsonrpc", jsonreq)


try:
    s.connect((host_ip, 22))
    if tv_open:
        pass
    else:
        print("resume all")
        resume_all()
        with open(status_file, 'w') as f:
            f.write("on")
except socket.error as e:
    if not tv_open:
        pass
    else:
        pause_all()
        print "pause all"
        os.remove(status_file)
finally:
    s.close()
