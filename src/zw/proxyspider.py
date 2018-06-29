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
class ProxySpider():
	def __init__(self, cfg_path, pool_size=4):
		self.cfg_path = cfg_path
		self.pool_size = pool_size
		self.cfg = cfg = Config(cfg_path).data
		self.urls = cfg['ippool']['urls']
		self.interval = cfg['ippool']['interval']
		self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'}
	
	def get_data(self, url):
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
		url = self.urls[0]
		r = requests.get(url, headers=self.headers)
		soup = BeautifulSoup(r.text, 'html.parser')
		pages = soup.find_all(attrs={'class': 'pagination'})
		if len(pages) == 0:
			LOG.debug('PROXY SOURCE BLOCK YOU')
			return
		pages = pages[0].contents
		last = int(pages[len(pages)-3].string)
		urls = [url]
		for i in range(2, last+1):
			urls.append(url + str(i))
		
		self.worker = wk = WorkerThread(urls, self.get_data, self.interval, self.pool_size)
		wk.start()
		#wk.join()

	def stop(self):
		self.worker.stop()

class WorkerThread(threading.Thread):
	def __init__(self, urls, proc_func, interval, pool_size=4):
		super(WorkerThread, self).__init__()
		self.urls = urls
		self.proc_func = proc_func
		self.interval = interval
		self.pool_size = pool_size
		self.thread_stop = False

	def run(self):
		self.thread_stop = False
		LOG.debug('Start proxy spider')
		step = 1
		urls = []
		for idx, url in enumerate(self.urls):
			if self.thread_stop:
				break
			urls.append(url)
			if idx % step == 0:
				LOG.debug(urls)
				pool = ThreadPool(self.pool_size)
				results = pool.map(self.proc_func, urls)
				# close the pool and wait for the work to finish
				pool.close()
				pool.join()
				urls[:] = []
				SIG_REFRESH.send(self)
				time.sleep(self.interval)
		LOG.debug('Finish proxy spider')

	def stop(self):
		self.thread_stop = True

if __name__ == '__main__':
	cfg_path = 'cfg.json'
	cfg = Config(cfg_path).data
	Database(cfg['database']).init_db()
	spider = ProxySpider(cfg_path)
	spider.start()

