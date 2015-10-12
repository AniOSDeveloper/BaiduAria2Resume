# BaiduAria2Resume

##总述
百度的链接有时效性，保持这个脚本在后台运行，修复失效链接。
![](https://raw.githubusercontent.com/sunzhaoyang/BaiduAria2Resume/master/screenshot.png)

##项目推荐
百度网盘的下载速度是有目共睹的，配合aria2下载一般都可以达到满速
推荐配合插件:

###BaiduExporter
<https://github.com/acgotaku/BaiduExporter>

可以方便的把百度云任务添加到aria2中。


###webui-aria2
<https://github.com/ziahamza/webui-aria2>

aria2 比较好的管理页面

###pan-baidu-download
<https://github.com/banbanchs/pan-baidu-download>

登陆部分代码来自pan-baidu-download项目，感谢原作者！

##参数

```
➜  BaiduAria2Resume git:(master) ✗ python baidu.py -h
usage: baidu.py [-h] -u UserName -p Password [-port Port] [-host HOST] [-r]
                [-i Id]

optional arguments:
  -h, --help   show this help message and exit
  -u UserName  Baidu User Name
  -p Password  Baidu Password
  -port Port   Aria2 server port,default:6800
  -host HOST   Aria2 host address,default:127.0.0.1
  -r           Refresh cache,shoule be true when file changes on pcs.
  -i Id        Aria2 download id #设定的aria2 id，每个用户不同，BaiduExporter用的是“aria2_download”，也是脚本的默认值.

```
####Tips
第一次使用会扫一遍百度云中的所有文件，速度比较慢。加了cache，第二次就不会扫了。但是如果百度云中的文件有变化，请加上 ”-r“ 选项刷新cache


####Example
```
python baidu.py -u username -p passwd -host 127.0.0.1 -port 6800 -r -i aria2_download
```




