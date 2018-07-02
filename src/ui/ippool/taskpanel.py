import time
import threading
from multiprocessing.dummy import Pool as ThreadPool
import wx
import wx.dataview as dv
import requests
from blinker import signal

import zw.images as images
from zw.database import Database
import zw.logger as logger

LOG = logger.getLogger(__name__)
SIG_TASK_RESULT = signal('task_result')
SIG_REFRESH = signal('refresh')

class TaskPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)
		self.init_ui()
		self.bind_event()

	def init_ui(self):
		self.dvc = dvc = dv.DataViewCtrl(self,
								   style=wx.BORDER_THEME
								   | dv.DV_ROW_LINES # nice alternating bg colors
								   #| dv.DV_HORIZ_RULES
								   | dv.DV_VERT_RULES
								   | dv.DV_MULTIPLE
								   )
		dvc.AppendTextColumn("待测IP", 1, width=120)
		dvc.AppendTextColumn("端口", 2, width=50)
		dvc.AppendTextColumn('连接类型', 3, width=100)
		dvc.AppendProgressColumn('测试结果', 4, width=100)
		dvc.SetIndent(0)
		for c in dvc.Columns:
			c.Sortable = True
			c.Reorderable = True
			c.MinWidth = 30
			# c.Alignment = wx.ALIGN_CENTER
			# c.Renderer.Alignment = wx.ALIGN_CENTER
		self.Sizer = wx.BoxSizer(wx.VERTICAL)
		self.Sizer.Add(dvc, 1, wx.EXPAND)

	def load_data(self):
		rows = self.get_all_record()
		self.model = TaskListModel(rows)
		# Tel the DVC to use the model
		self.dvc.AssociateModel(self.model)
	
	def bind_event(self):
		SIG_TASK_RESULT.connect(self.on_task_result)

	def on_task_result(self, dat):
		wx.CallAfter(self.update_status, dat)

	def update_status(self, dat):
		result = dat['result']
		rec = dat['rec']
		rec[4] = 1 if result else 0 # set valid field
		self.update_record(rec)
		self.model.update_row(rec)

	def do_task(self, rec):
		ip = rec[1]
		port = rec[2]
		conn_type = rec[3]
		conn_type = conn_type.lower() if conn_type else 'http'
		proxies = {'http': 'http://%s:%s' % (ip, port)} if conn_type == 'http' else\
					 {'https': 'http://%s:%s' % (ip, port)}
		try:
			r = requests.get('http://www.baidu.com', proxies=proxies, timeout=5)
		except:
			SIG_TASK_RESULT.send({'rec': rec, 'result': False})
			SIG_REFRESH.send(self)
			return
		result = True if r.status_code == 200 else False
		SIG_TASK_RESULT.send({'rec': rec, 'result': result})
		SIG_REFRESH.send(self)

	def start_worker(self):
		self.load_data()
		self.worker = TaskWorkerThread(self.model.data, self.do_task)
		self.worker.start()

	def stop_worker(self):
		self.worker.stop()

	def get_all_record(self):
		db = Database()
		rows = db.query('ippool_all')
		rows = rows.as_dict()
		rows = [ [i, d['ip'], d['port'], d['conn_type'], d['valid'] ] for i, d in enumerate(rows)]
		return rows
	
	def update_record(self, rec):
		ip = rec[1]
		port = rec[2]
		valid = rec[4]
		db = Database()
		rows = db.query('ippool_update_valid', ip=ip, port=port, valid=valid)

class TaskListModel(dv.DataViewIndexListModel):
	def __init__(self, data):
		dv.DataViewIndexListModel.__init__(self, len(data))
		self.data = data
		
	def GetColumnType(self, col):
		'''
		string bool datetime
		'''
		return 'string'

	def GetValueByRow(self, row, col):
		return self.data[row][col]
	
	def GetColumnCount(self):
		return len(self.data[0])
	
	def GetCount(self):
		return len(self.data)
		
	def GetAttrByRow(self, row, col, attr):
		return False
		
	def SetValueByRow(self, value, row, col):
		'''
		readonly grid return true
		'''
		return True

	def Compare(self, item1, item2, col, ascending):
		if not ascending: # swap sort order?
			item2, item1 = item1, item2
		row1 = self.GetRow(item1)
		row2 = self.GetRow(item2)
		return self.data[row1][col] < self.data[row2][col]

	def update_row(self, rec):
		idx = rec[0]
		self.data[idx][4] = rec[4]*100
		self.RowChanged(idx)

class TaskWorkerThread(threading.Thread):
	def __init__(self, dat, proc_func, interval=3, pool_size=3):
		super(TaskWorkerThread, self).__init__()
		self.dat = dat
		self.proc_func = proc_func
		self.interval = interval
		self.pool_size = pool_size
		self.thread_stop = False

	def run(self):
		self.thread_stop = False
		LOG.debug('Start task thread')
		step = 5
		proxys = []
		for idx, proxy in enumerate(self.dat):
			if self.thread_stop:
				break
			proxy.append(idx)
			proxys.append(proxy)
			if idx % step == 0:
				pool = ThreadPool(self.pool_size)
				results = pool.map(self.proc_func, proxys)
				# close the pool and wait for the work to finish
				pool.close()
				pool.join()
				proxys[:] = []
				time.sleep(self.interval)
		LOG.debug('Finish task thread')

	def stop(self):
		self.thread_stop = True
