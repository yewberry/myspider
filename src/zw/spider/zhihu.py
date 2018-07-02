import time
import threading
from multiprocessing.dummy import Pool as ThreadPool
import requests
from bs4 import BeautifulSoup
from blinker import signal

if __name__ == '__main__':
	import sys;import os;sys.path.insert(0, os.path.dirname(sys.path[0]))

from zw.config import Config
from zw.database import Database
import zw.logger as logger

SIG_REFRESH = signal('refresh')

LOG = logger.getLogger(__name__)
class ZhihuSpider():
	def __init__(self, start_idx=0, pool_size=5):
		self.start_idx = start_idx
		self.pool_size = pool_size
		self.url = 'https://www.zhihu.com/question/'
		self.interval = 5
		self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
		self.worker = None
	
	def thread_func(self, url):
		db = Database()
		r = requests.get(url, headers=self.headers)
		soup = BeautifulSoup(r.text, 'html.parser')
		items = soup.find_all(self.find_tag)
		LOG.debug('found %s' % len(items))
		recs = []
		for p in items:
			cts = p.contents
			ip = cts[3].string if cts[3].string else ''
			port = cts[5].string if cts[5].string else ''
			city = cts[7].a.string if cts[7].a else ''
			conn_type = cts[11].string if cts[11].string else ''
			speed = cts[13].div['title']
			speed = speed[:len(speed)-1]
			o = {'ip':ip, 'port':port, 'country':'cn', 'city':city, 'speed':speed, 'conn_type':conn_type}
			recs.append(o)
		num_insert, num_update = db.insert_update(recs, 'ippool_exist', 'ippool_insert', 'ippool_update', ['ip','port'])
	
	def find_tag(self, tag):
		return tag.name == 'tr' and tag.has_attr('class')

	def start(self):
		url = self.url
		urls = []
		first = self.start_idx
		last = 1000000000
		for i in range(first, last):
			urls.append(url + str(i))
		
		self.worker = wk = WorkerThread(urls, self.thread_func, self.interval, self.pool_size)
		wk.start()
		wk.join()

	def stop(self):
		self.worker.stop()

class WorkerThread(threading.Thread):
	def __init__(self, urls, proc_func, interval, pool_size):
		threading.Thread.__init__(self)
		self.urls = urls
		self.proc_func = proc_func
		self.interval = interval
		self.pool_size = pool_size
		self.thread_stop = False

	def run(self):
		self.thread_stop = False
		LOG.debug('Start zhihu spider')
		step = self.pool_size
		urls = []
		for idx, url in enumerate(self.urls):
			if self.thread_stop:
				break
			urls.append(url)
			if idx % step == 0:
				LOG.debug('========================================')
				LOG.debug(urls)
				pool = ThreadPool(self.pool_size)
				results = pool.map(self.proc_func, urls)
				# close the pool and wait for the work to finish
				pool.close()
				pool.join()
				urls[:] = []
				SIG_REFRESH.send(self)
				time.sleep(self.interval)
		LOG.debug('Finish zhihu spider')

	def stop(self):
		self.thread_stop = True

if __name__ == '__main__':
	cfg_path = 'cfg.json'
	cfg = Config(cfg_path).data
	idx = cfg['zhihu']['curidx']
	spider = ZhihuSpider()
	spider.start()

