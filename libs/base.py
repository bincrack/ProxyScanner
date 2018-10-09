#-*- coding:utf-8 -*-
'''
	@name	Base Functions
	@modify	2014/11/27
	@author	Holger
	@github	https://github.com/h01/ProxyScanner
	@myblog	http://ursb.org
'''
from pycui  import *
from genips import genips
import Queue, threading
import urllib2, socket
import itertools

cui = pycui()
gen = genips()
cor = color()

class Num:
	def __init__(self, num = 0):
		self.num = num
		self.lock = threading.Lock()
	def add(self):
		self.lock.acquire()
		self.num += 1
		self.lock.release()
		return self.num

class base:
	def __init__(self):
		self._p = [8080]
		self._t = 10
		self._i = []
		self._ip = []
		self._o = []
		self._r = []
		self._s = ''
		self._f = ''
		self._n1 = Num()
		self._n2 = Num()

	def run(self, opts):
		for k, v in opts:
			if k in ['-v', '--version']:
				self.version()
			elif k in ['-p', '--port']:
				_temp = v.split(',')
				self._p = map(lambda x : int(x), _temp)
			elif k in ['-i', '--ips']:
				_temp = v.split('-')
				self._ip = gen.gen(_temp[0], _temp[1])
			elif k in ['-t', '--thread']:
				self._t = int(v)
			elif k in ['-s', '--save']:
				self._s = v
			elif k in ['-f', '--file']:
				self._f = v
			else:
				self.usage()
		if self._f != '':
			with open(self._f, 'r') as fp:
				for item in fp.readlines():
					_temp = item.strip().split(':')
					self._i.append((_temp[0], _temp[1]))
		else:
			for item in self._ip:
				self._i = self._i + (map(lambda x : (item, x), self._p))
		if (200 >= self._t > 0) and (len(self._i) > 0):
			self.start()
		else:
			self.usage()
	def start(self):
		cui.w('Proxy Scanner started')
		cui.i('File: %s'%self._f)
		cui.i('Nums: %s'%len(self._i))
		cui.i('Port: %s'%self._p)
		cui.i('Thread: %s'%self._t)
		self.scanports()
		self.scanproxy()
		self.result()
	def scanports(self):
		cui.w('Start scanning the open port\'s IP..')
		def run(q):
			while not q.empty():
				_ip = q.get()
				if self.checkPort(_ip[0], _ip[1]):
					cui.s('Open: %s:%s\t\t%s/%s'%(_ip[0], _ip[1], self._n1.add(), len(self._i)))
					self._o.append(_ip)
				else:
					cui.e('Close: %s:%s\t\t%s/%s'%(_ip[0], _ip[1], self._n1.add(), len(self._i)))
		self.startThread(self._i, run)

	def scanproxy(self):
		if len(self._o) > 0:
			cui.w('Checking the proxy is available..')
			def run(q):
				while not q.empty():
					_ip = q.get()
					if self.checkProxy(_ip[0], _ip[1]):
						cui.s('OK: %s:%s\t\t%s/%s'%(_ip[0], _ip[1], self._n2.add(), len(self._o)))
						self._r.append(_ip)
					else:
						cui.e('NO: %s:%s\t\t%s/%s'%(_ip[0], _ip[1], self._n2.add(), len(self._o)))
			self.startThread(self._o, run)
		else:
			cui.i('Not proxy to checking..')
	def startThread(self, arr, func):
		__q = Queue.Queue()
		__t = []
		for ip in arr:
			__q.put(ip)
		for i in range(self._t):
			__t.append(threading.Thread(target = func, args = (__q, )))
		for i in range(self._t):
			__t[i].setDaemon(True)
			__t[i].start()
		for i in range(self._t):
			__t[i].join(timeout = 10)
			cui.i("%s Done" % __t[i].name)
	def checkPort(self, host, port):
		try:
			_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			_s.settimeout(3)
			_s.connect((host, int(port)))
			_s.close()
			return True
		except:
			return False
	def checkProxy(self, h, p):
		_p = "http://%s:%s"%(h, p)
		_h = urllib2.ProxyHandler({'http': _p})
		_o = urllib2.build_opener(_h, urllib2.HTTPHandler)
		try:
			_r = _o.open('https://www.baidu.com/img/baidu_jgylogo3.gif', timeout = 5)
			_t = _r.read()
			_l = len(_t)
			if _l == 705:
				return True
			return False
		except Exception,e:
			return False
	def result(self):
		cui.i('Scan result: %s' % len(self._r))
		if len(self._r) > 0:
			for _r in self._r:
				print "\t%s:%s"%(_r)
			if self._s != '':
				_f = open(self._s, 'a')
				for _r in self._r:
					_f.write('%s:%s\n'%(_r))
				_f.close()
				cui.s('Save as (%s)'%self._s)
		exit(0)
	def banner(self):
		return '''\
	______                    _____                                 
	| ___ \                  /  ___|                                
	| |_/ / __ _____  ___   _\ `--.  ___ __ _ _ __  _ __   ___ _ __ 
	|  __/ '__/ _ \ \/ / | | |`--. \/ __/ _` | '_ \| '_ \ / _ \ '__|
	| |  | | | (_) >  <| |_| /\__/ / (_| (_| | | | | | | |  __/ |   
	\_|  |_|  \___/_/\_\\\\__, \____/ \___\__,_|_| |_|_| |_|\___|_|   
	                     __/ |                                      
	                    |___/                                       '''
	def usage(self):
		cor.p(self.banner(), cor.RED)
		cor.p('PS 1.0 (Proxy Scanner)', cor.GREEN)
		cor.p('\tAuthor: Holger', cor.YELLOW)
		cor.p('\tModify: 2014/11/27', cor.YELLOW)
		cor.p('\tGitHub: https://github.com/h01/ProxyScanner', cor.YELLOW)
		cor.p('\tMyBlog: http://ursb.org', cor.YELLOW)
		cor.p('\tVersion: 1.0', cor.RED)
		cor.p('Usage: ./ps [args] [value]', cor.GREEN)
		cor.p('Args: ', cor.PURPLE)
		cor.p('\t-v --version\t\tPS version')
		cor.p('\t-h --help\t\tHelp menu')
		cor.p('\t-i --ips\t\tIPS: 192.168.1.1-192.168.1.100')
		cor.p('\t-p --port\t\tProxy port (default:8080)')
		cor.p('\t-t --thread\t\tScan thread (default:10)')
		cor.p('\t-s --save\t\tSave scan result')
		exit(0)
	def version(self):
		cui.i('ProxyScanner version 1.0')
		exit(0)