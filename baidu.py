# coding=utf-8
import base64
import json
import re
import login
from time import time
import urllib
import sys
import urllib2
import hashlib
import os
import argparse

reload(sys)
sys.setdefaultencoding("utf8")


class BaiduResume:
    def __init__(self, user_name, passwd, host="127.0.0.1", port=6800, aria2_id="aria2_download"):
        self.user_name = user_name
        self.passwd = passwd
        self.host = host
        self.port = port
        self.list_url = "http://pan.baidu.com/api/list?channel=chunlei&clienttype=0&web=1&num=100&page=1&order=time&desc=1&showempty=0&channel=chunlei&clienttype=0&web=1&"
        self.download_url = "http://pan.baidu.com/api/download?type=dlink&channel=chunlei&clienttype=0&web=1&"
        self.account = login.login([self.user_name, self.passwd])
        self.session = self.account.session
        self.all_file_fid = {}  # {filename_hash:[fid,path]}
        self.aria2_url = 'http://%s:%d/jsonrpc' % (self.host, self.port)
        self.aria2_id = aria2_id
        self.aria2_header = "Cookie:BDUSS=" + self.account.bduss
        self.cache_path = os.path.expanduser("~/.baidu.cache")

    def _get_all_file_fid(self, path):
        list_params = urllib.urlencode({"dir": path, "_": int(time()), "bdstoken": self.account.token})
        response = self.session.get(self.list_url + list_params)
        list_data = json.loads(response.text)
        for sub_path in list_data.get("list"):
            sub_path_name = sub_path['server_filename']
            if sub_path['isdir']:
                if not sub_path['empty']:
                    self._get_all_file_fid(path + sub_path_name + "/")
            else:
                fs_id = sub_path['fs_id']
                self.all_file_fid[get_hash_code(sub_path_name)] = fs_id

    def _aria2_rpc_error_task(self):
        jsonreq = json.dumps({'jsonrpc': '2.0', "id": self.aria2_id,
                              'method': 'aria2.tellStopped', 'params': [0, 65536, ['files', 'dir', 'status', 'gid']]})
        res = urllib2.urlopen(self.aria2_url, jsonreq).read()
        all_stoped = json.loads(res).get("result")
        if all_stoped:
            for item in all_stoped:
                if item.get("status") == "error":
                    dl_dir = item.get("dir")
                    gid = item.get("gid")
                    path = item.get("files")[0].get("path")
                    uri = item.get("files")[0].get("uris")[0].get("uri")
                    fid = self._get_fid_from_uri(uri)
                    baidu_path = path.replace(dl_dir, "")
                    result = self._aria2_rpc_add_uri(self._get_download_link(fid),
                                                     self.aria2_header, dl_dir, baidu_path[1:])
                    self._aria2_rpc_remove(gid)

    @staticmethod
    def _get_fid_from_uri(uri):
        match = re.search(r"fid=[^-]+-[^-]+-([^&]+)&", uri)
        if match:
            return match.group(1)
        return None

    def _aria2_rpc_add_uri(self, dlink, header, dl_dir, out):
        jsonreq = json.dumps({'jsonrpc': '2.0', "id": self.aria2_id,
                              'method': 'aria2.addUri', 'params': [[dlink],
                                                                   {'header': header, 'dir': dl_dir,
                                                                    'out': out}]})
        res = urllib2.urlopen(self.aria2_url, jsonreq)
        return json.loads(res.read())

    def _aria2_rpc_remove(self, gid):
        jsonreq = json.dumps({'jsonrpc': '2.0', 'id': self.aria2_id, 'method': 'aria2.removeDownloadResult',
                              'params': [str(gid)]})
        res = urllib2.urlopen(self.aria2_url, jsonreq)
        return json.loads(res.read())

    def _get_download_link(self, fid):
        url = self.download_url + urllib.urlencode(
            {"timestamp": int(time()), "fidlist": "[" + str(fid) + "]",
             "bdstoken": self.account.token,
             "sign": self._get_sign()})
        response = self.session.get(url)
        json_data = json.loads(response.text)
        if json_data['errno'] == 0:
            dlink = json_data.get('dlink')[0].get('dlink')
            return dlink
        else:
            print response.text
        return None

    def _get_sign(self):
        res = self.session.get("http://pan.baidu.com/disk/home").content
        sign1 = re.search(r'yunData.sign1\s=\s\'(.*?)\';', res).group(1)
        sign3 = re.search(r'yunData.sign3\s=\s\'(.*?)\';', res).group(1)
        timestamp = re.search(r'timestamp = \'(.+?)\';', res).group(1)

        def sign2(j, r):
            a = []
            p = []
            o = ''
            v = len(j)
            for q in xrange(256):
                a.append(ord(j[(q % v)]))
                p.append(q)

            u = 0
            for q in xrange(256):
                u = (u + p[q] + a[q]) % 256
                p[q], p[u] = p[u], p[q]

            i = 0
            u = 0
            for q in xrange(len(r)):
                i = (i + 1) % 256
                u = (u + p[i]) % 256
                p[i], p[u] = p[u], p[i]
                k = p[((p[i] + p[u]) % 256)]
                o += chr(ord(r[q]) ^ k)
            return base64.b64encode(o)

        return sign2(sign3, sign1)

    def start(self):
        self._aria2_rpc_error_task()


def get_hash_code(s):
    key = hashlib.md5()
    key.update(s)
    return key.hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", dest="username", metavar="UserName", required=True, help="Baidu User Name")
    parser.add_argument("-p", dest="passwd", metavar="Password", required=True, help="Baidu Password")
    parser.add_argument("-port", dest="port", metavar="Port", default=6800, type=int, required=False,
                        help="Aria2 server port,default:6800")
    parser.add_argument("-host", dest="host", default="127.0.0.1", help="Aria2 host address,default:127.0.0.1")
    parser.add_argument("-i", dest="aria2_id", metavar="Id", default="aria2_download",
                        help="Aria2 download id.default:aria2_download")
    args = parser.parse_args()

    resume = BaiduResume(user_name=args.username, passwd=args.passwd, host=args.host,
                         port=args.port, aria2_id=args.aria2_id)
    resume.start()
