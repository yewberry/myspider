import wx
import wx.ribbon as RB
import wx.dataview as dv

import zw.images as images
import zw.utils as utils
from zw.spider.proxy import ProxySpider

import ui.trayicon as trayicon
from ui.ippool.poolpanel import PoolPanel
from ui.settingdialog import SettingDialog

ID_RIBBON		= wx.ID_HIGHEST + 1
ID_IP_POOL 		= ID_RIBBON + 1
ID_IP_TEST 		= ID_RIBBON + 2
ID_IP_SETTING 	= ID_RIBBON + 3
ID_ZH_START 	= ID_RIBBON + 4
ID_PAGE_IP		= ID_RIBBON + 5
ID_PAGE_ZH		= ID_RIBBON + 6

class RibbonFrame(wx.Frame):
	def __init__(self, parent, id=wx.ID_ANY, title='', pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
		wx.Frame.__init__(self, parent, id, title, pos, size, style)
		self.toggles_ids= [ID_IP_POOL, ID_IP_TEST]
		self.pages_ids = [ID_PAGE_IP, ID_PAGE_ZH]
		self.init_ui()
		self.bind_events()

	
	def init_ui(self):
		if utils.isWin32():
			self._tbIcon = trayicon.TrayIcon(self, images.logo48.Icon)
		self._root_panel = wx.Panel(self)
		self._panel = wx.Panel(self._root_panel)
		self._ribbon = RB.RibbonBar(self._root_panel, ID_RIBBON, style=RB.RIBBON_BAR_DEFAULT_STYLE | RB.RIBBON_BAR_SHOW_PANEL_EXT_BUTTONS)

		rb_page = RB.RibbonPage(self._ribbon, ID_PAGE_IP, 'IP代理地址池')

		rb_panel = RB.RibbonPanel(rb_page, wx.ID_ANY, 'IP工具', style=RB.RIBBON_PANEL_NO_AUTO_MINIMISE | RB.RIBBON_PANEL_EXT_BUTTON)
		rb_bar = RB.RibbonButtonBar(rb_panel, wx.ID_ANY)
		rb_bar.AddToggleButton(ID_IP_POOL, 'IP代理爬取', images.pool.Bitmap)
		rb_bar.AddToggleButton(ID_IP_TEST, 'IP代理测试', images.test.Bitmap)

		rb_panel = RB.RibbonPanel(rb_page, wx.ID_ANY, '设置')
		rb_bar = RB.RibbonButtonBar(rb_panel, wx.ID_ANY)
		rb_bar.AddButton(ID_IP_SETTING, '设置', images.setting.Bitmap)

		rb_page = RB.RibbonPage(self._ribbon, ID_PAGE_ZH, '知乎')
		rb_panel = RB.RibbonPanel(rb_page, wx.ID_ANY, '知乎工具', style=RB.RIBBON_PANEL_NO_AUTO_MINIMISE | RB.RIBBON_PANEL_EXT_BUTTON)
		rb_bar = RB.RibbonButtonBar(rb_panel, wx.ID_ANY)
		rb_bar.AddToggleButton(ID_ZH_START, '知乎爬取', images.pool.Bitmap)

		self._ribbon.Realize()
		self.set_ribbon_page(ID_PAGE_IP)

		#--------------------------------------------------------------
		self.proxyspider = ProxySpider(wx.GetApp().cfg_path)
		#--------------------------------------------------------------

		s = wx.BoxSizer(wx.VERTICAL)
		s.Add(self._ribbon, 0, wx.EXPAND)
		s.Add(self._panel, 1, wx.EXPAND)
		#s.Add(self.poolpanel, 1, wx.EXPAND)
		self._root_panel.SetSizer(s)

		self.SetIcon(images.logo48.Icon)
		self.CenterOnScreen()
		self.set_art_provider(RB.RibbonMSWArtProvider())

	def bind_events(self, bars=None):
		# bar0, bar1 = bars
		# toggle toolbar click
		for btn_id in self.toggles_ids:
			self.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.on_toogle_click, id=btn_id)
		
		self.Bind(RB.EVT_RIBBONBAR_PAGE_CHANGING, self.on_page_changing, id=ID_RIBBON)
		self.Bind(RB.EVT_RIBBONBAR_PAGE_CHANGED, self.on_page_changed, id=ID_RIBBON)
		
		#self.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.poolpanel.statpanel.onAddRow, id=ID_IP_SETTING)
		self.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.on_setting_click, id=ID_IP_SETTING)

		if utils.isWin32():
			self.Bind(wx.EVT_ICONIZE, self.on_iconify)
		self.Bind(wx.EVT_CLOSE, self.on_close)
	
	def set_ribbon_page(self, page_id):
		idx = 0
		if page_id == ID_PAGE_IP:
			self.poolpanel = PoolPanel(self._panel, wx.ID_ANY)
			panel_sizer = wx.BoxSizer(wx.VERTICAL)
			panel_sizer.Add(self.poolpanel, 1, wx.EXPAND)
			self._panel.SetSizer(panel_sizer)
			idx = 0
		elif page_id == ID_PAGE_ZH:
			idx = 1
		self._ribbon.SetActivePage(idx)
		self._panel.Layout()

	def on_toogle_click(self, event):
		tool_id = event.GetId()
		print( 'tool:{0}, state:{1}'.format( tool_id, event.IsChecked()) )
		if tool_id == ID_IP_POOL:
			if event.IsChecked():
				self.proxyspider.start()
			else:
				self.proxyspider.stop()
		elif tool_id == ID_IP_TEST:
			if event.IsChecked():
				self.poolpanel.start_task()
			else:
				self.poolpanel.stop_task()
	
	def on_page_changing(self, event):
		for child in self._panel.GetChildren():
			child.Destroy()

	def on_page_changed(self, event):
		page_id = event.GetPage().GetId()
		self.set_ribbon_page(page_id)

	def on_setting_click(self, event):
		dlg = SettingDialog(self, -1, '配置', size=(350, 200))
		dlg.ShowWindowModal()

	def on_iconify(self, event):
		self.Hide()

	def on_close(self, event):
		'''
		Destroy the taskbar icon and the frame
		'''
		if utils.isWin32():
			self._tbIcon.RemoveIcon()
			self._tbIcon.Destroy()
		self.Destroy()

	def set_art_provider(self, prov):
		self._ribbon.DismissExpandedPanel()
		self._ribbon.Freeze()
		self._ribbon.SetArtProvider(prov)
		self._ribbon.Thaw()
		self._ribbon.Realize()
