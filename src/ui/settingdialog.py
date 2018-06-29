import wx
from zw.config import Config
import zw.database as database

class SettingDialog(wx.Dialog):
	def __init__(self, parent, id, title, pos=wx.DefaultPosition, size=wx.DefaultSize
				, style=wx.DEFAULT_DIALOG_STYLE):
		wx.Dialog.__init__(self, parent, id, title, pos, size, style)
		self.cfg = cfg = Config(wx.GetApp().cfg_path)
		self.init_ui()
		self.bind_events()
		self.on_dbtype_select(None)
	
	def init_ui(self):
		cdat = self.cfg.data
		o = cdat['database']
		nb = wx.Notebook(self, -1, size=(500, 300))
		p = wx.Panel(nb, -1)

		fgs = wx.FlexGridSizer(4, 4, 9, 25)
		lb1 = wx.StaticText(p, -1, '数据库类型:')
		ct1 = wx.ComboBox(p, -1, style=wx.CB_DROPDOWN|wx.CB_READONLY
						, choices=['sqlite', 'mysql'], value=o['dbtype'])
		lb2 = wx.StaticText(p, -1, '数据库名:')
		ct2 = wx.TextCtrl(p, -1, o['dbname'])
		lb4 = wx.StaticText(p, -1, '用户名:')
		ct4 = wx.TextCtrl(p, -1, o['dbuser'])
		lb5 = wx.StaticText(p, -1, '密码:')
		ct5 = wx.TextCtrl(p, -1, o['dbpass'])
		lb6 = wx.StaticText(p, -1, '数据表地址:')
		ct6 = wx.TextCtrl(p, -1, o['dbaddr'])
		fgs.AddMany([
			(lb1, 0, wx.ALIGN_RIGHT), (ct1, 0, wx.EXPAND),
			(lb2, 0, wx.ALIGN_RIGHT), (ct2, 0, wx.EXPAND),
			(lb4, 0, wx.ALIGN_RIGHT), (ct4, 0, wx.EXPAND),
			(lb5, 0, wx.ALIGN_RIGHT), (ct5, 0, wx.EXPAND),
			(lb6, 0, wx.ALIGN_RIGHT), (ct6, 0, wx.EXPAND),
		])
		fgs.AddGrowableCol(1, 1)
		fgs.AddGrowableCol(3, 1)

		self.dbtype = ct1
		self.dbname = ct2
		self.dbuser = ct4
		self.dbpass = ct5
		self.dbaddr = ct6

		ps = wx.BoxSizer(wx.VERTICAL)
		ps.Add(fgs, 0, wx.EXPAND)
		p.SetSizer(ps)
		nb.AddPage(p, '地址池设置')

		p = wx.Panel(nb, -1)
		nb.AddPage(p, '域名设置')

		btnsizer = wx.StdDialogButtonSizer()
		btn = wx.Button(self, wx.ID_OK)
		btnsizer.AddButton(btn)
		btn = wx.Button(self, wx.ID_CANCEL)
		btn.SetDefault()
		btnsizer.AddButton(btn)
		btnsizer.Realize()

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(nb, 1, wx.EXPAND)
		sizer.Add(btnsizer, 0, wx.ALIGN_RIGHT|wx.ALL, 5)
		self.SetSizerAndFit(sizer)

	def bind_events(self):
		self.Bind(wx.EVT_BUTTON, self.on_ok_click, id=wx.ID_OK)
		self.dbtype.Bind(wx.EVT_COMBOBOX, self.on_dbtype_select)
	
	def on_ok_click(self, event):
		dat = self.cfg.data
		dat['ippool']['dbtype'] = self.dbtype.GetValue()
		dat['ippool']['dbname'] = self.dbname.GetValue()
		dat['ippool']['dbuser'] = self.dbuser.GetValue()
		dat['ippool']['dbpass'] = self.dbpass.GetValue()
		dat['ippool']['dbaddr'] = self.dbaddr.GetValue()
		self.cfg.save()
		database.init_db(wx.GetApp().cfg_path)
		self.Destroy()
	
	def on_dbtype_select(self, event):
		sel = self.dbtype.GetStringSelection()
		arr = [self.dbuser, self.dbpass, self.dbaddr]
		if 'sqlite' == sel:
			for p in arr:
				p.Disable()
		else:
			for p in arr:
				p.Enable()		
		

