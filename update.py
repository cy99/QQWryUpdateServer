#coding:utf-8
import time
import os
import json
import httplib2
import qqwry

import qiniu.conf
import qiniu.rs
import qiniu.io

qiniu.conf.ACCESS_KEY = ""
qiniu.conf.SECRET_KEY = ""

http = httplib2.Http(timeout=30)

config = "list.json"
def read_list():
	try:
		f = open(config, "r")
		s = json.load(f)
		f.close()
		return s
	except Exception, e:
		pass
	return {}

def save_list(date):
	date = str(date)
	datelist = read_list()
	datelist[date] = True
	f = open(config, "w")
	json.dump(datelist, f)
	f.close()

def make_patch(new):
	datelist = read_list()
	for old in datelist:
		print "make_patch ", old, new
		db1 = open("data/" + old + ".dat", "rb")
		db2 = open("data/" + new + ".dat", "rb")
		qqwry.make_patch(db1.read(), db2.read())
		db1.close()
		db2.close()

		#上传补丁
		print("upload patch " + new + "/" + old + ".db")
		ret, err = qiniu.io.put_file(qiniu.rs.PutPolicy("qqwry").token(), new + "/" + old + ".db", "patch/" + old + "-" + new + ".db")
		if err is not None:
			sys.stderr.write('error: %s ' % err)

def get_qqwry(date, copywrite):
	resp, content = http.request("http://update.cz88.net/ip/qqwry.rar", headers={'cache-control':'no-cache', 'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'})
	data = qqwry.decode(copywrite, content)
	out = open("data/" + date + ".dat", "wb")
	out.write(data)
	out.close()

def check_update():
	#下载元文件，查看最新版属性
	print "request copywrite.rar"
	resp, copywrite = http.request("http://update.cz88.net/ip/copywrite.rar", headers={'cache-control':'no-cache', 'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36'})
	print "parse copywrite.rar"
	date = qqwry.meta_parse(copywrite)
	date = str(date)
	print("check " + date)
	#本地无此版本
	if date not in read_list():
		#下载最新版数据
		print("begin download " + date)
		get_qqwry(date, copywrite)
		#制作此版本补丁
		print("begin make_patch " + date)
		make_patch(date)
		#保存列表
		save_list(date)
		print("update " + date)

try:
	os.makedirs("data")
	os.makedirs("patch")
except Exception:
	pass

def timer(sec):
	while True:
		print time.strftime('\ntask %Y-%m-%d %X',time.localtime())
		try:
			check_update()
		except Exception, e:
			print e
		time.sleep(sec)

if __name__ == "__main__":
	timer(10*60) #10分钟检查一次