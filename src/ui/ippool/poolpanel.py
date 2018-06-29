import wx
from blinker import signal

from zw.database import Database
from ui.ledctrl import LEDCtrl
from ui.ippool.statpanel import StatPanel
from ui.ippool.taskpanel import TaskPanel

SIG_LOG = signal('log')
SIG_REFRESH = signal('refresh')
SIG_TASK_RESULT = signal('task_result')

class PoolPanel(wx.Panel):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition
				, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL):
		wx.Panel.__init__(self, parent, id, pos, size, style)
		self.init_ui()
		self.load_data()
		self.bind_event()
	
	def init_ui(self):
		led_size = (100, 50)
		self.led_total = LEDCtrl(self, -1, size=led_size, fgcolor='white')
		self.led_succ = LEDCtrl(self, -1, size=led_size)
		self.led_fail = LEDCtrl(self, -1, size=led_size, fgcolor='yellow')
		bsizer1 = wx.BoxSizer(wx.HORIZONTAL)
		bsizer1.Add(self.led_total, 1, wx.ALIGN_CENTER)
		bsizer1.Add(self.led_succ, 1, wx.ALIGN_CENTER)
		bsizer1.Add(self.led_fail, 1, wx.ALIGN_CENTER)

		
		self.statpanel = statpanel = StatPanel(self)
		self.taskpanel = taskpanel = TaskPanel(self)
		self.logwindow = logwindow = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)

		bsizer3 = wx.BoxSizer(wx.VERTICAL)
		bsizer3.Add(taskpanel, 1, wx.EXPAND)
		bsizer3.Add(logwindow, 1, wx.EXPAND)
		bsizer2 = wx.BoxSizer(wx.HORIZONTAL)
		bsizer2.Add(statpanel, 1, wx.EXPAND, border=10)
		bsizer2.Add(bsizer3, 1, wx.EXPAND, border=10)

		s = wx.BoxSizer(wx.VERTICAL)
		s.Add(bsizer1, 0, wx.EXPAND)
		s.Add(bsizer2, 1, wx.EXPAND)
		self.SetSizer(s)

	def load_data(self):
		db = Database()
		rs = db.query('ippool_count')
		self.led_total.SetValue(str(rs[0].c))
	
	def bind_event(self):
		SIG_REFRESH.connect(self.refresh)
		SIG_TASK_RESULT.connect(self.on_task_result)
		SIG_LOG.connect(self.on_log)
	
	def start_task(self):
		self.load_data()
		db = Database()
		rs = db.query('ippool_count_succ')
		self.led_succ.SetValue(str(rs[0].c))
		rs = db.query('ippool_count_fail')
		self.led_fail.SetValue(str(rs[0].c))
		self.taskpanel.start_worker()
	
	def stop_task(self):
		self.taskpanel.stop_worker()

	def refresh(self, sender):
		wx.CallAfter(self.load_data)
	def on_task_result(self, dat):
		wx.CallAfter(self.update_led, dat['result'])
	def on_log(self, dat):
		s = '%s\n' % dat
		wx.CallAfter(self.logwindow.write, s)
	
	def update_led(self, dat):
		led = self.led_succ if dat else self.led_fail
		val = 1 if dat else -1
		val = int(led.GetValue()) + val
		led.SetValue(str(val))

		