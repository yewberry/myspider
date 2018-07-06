import os
import wx
import zw.logger as logger
from zw.utils import Timeit
from ui.ribbonframe import RibbonFrame
from zw.config import Config
from zw.database import Database

LOG = logger.getLogger(__name__)
class App(wx.App):
	cfg_path = property(lambda s: s._cfg_path, lambda s, v: setattr(s, '_cfg_path', v))

	def OnInit(self):
		t = Timeit()
		LOG.debug("OnInit")
		self.cfg_path = 'cfg.json'
		# init config file
		cfg = Config(self.cfg_path, {
			'version': '1.0.0',
			'database': {
				'dbtype': 'sqlite',
				'dbname': 'data.db',
				'dbuser': '',
				'dbpass': '',
				'dbaddr': 'localhost',
			},
			'ippool': {
				'urls': ['http://www.xicidaili.com/nn/'],
				'interval': 60,
			}
		}).data
		# init db
		Database(cfg['database']).init_db()

		frm = RibbonFrame(None, -1, '爬虫工具集 v0.1 yew1998@gmail.com', size=(1024, 768))
		frm.Show()
		LOG.debug('Elapsed time: %f ms' % t.end())
		return True

	def OnExit(self):
		# exit but main process still there why?
		wx.Exit()




