import sys
import time
import multiprocessing

import requests
from bs4 import BeautifulSoup
from blinker import signal

if __name__ == '__main__':
	import sys;import os;sys.path.insert(0, os.path.dirname(os.path.dirname(sys.path[0])))

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
	
	def check_pages_exist(self, idx, rtn):
		url = self.url + idx
		r = requests.head(url)
		a = 0

	def test(self, i):
		print(i)
		time.sleep(3)
		return 'process %s return' % i
	
	def start(self):
		print( 'start in %s processes' % multiprocessing.cpu_count() )
		arr = range(10)
		rs = []
		pool = multiprocessing.Pool(multiprocessing.cpu_count())
		# poll.map_async(self.test, arr)
		for i in range(100):
			rs.append( pool.apply_async(self.test, args=(i,)) )
		pool.close()
		pool.join()
		for res in result:
			print( '::: %s' % res.get() )

	def stop(self):
		self.worker.stop()


if __name__ == '__main__':
	spider = ZhihuSpider()
	spider.start()

