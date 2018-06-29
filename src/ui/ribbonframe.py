import wx
import wx.ribbon as RB
import wx.dataview as dv

import zw.images as images
import zw.utils as utils
from zw.proxyspider import ProxySpider

import ui.trayicon as trayicon
from ui.ippool.poolpanel import PoolPanel
from ui.settingdialog import SettingDialog

ID_IP_POOL= wx.ID_HIGHEST + 1
ID_IP_TEST = ID_IP_POOL + 1
ID_IP_SETTING = ID_IP_POOL + 3

class RibbonFrame(wx.Frame):
	def __init__(self, parent, id=wx.ID_ANY, title='', pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
		wx.Frame.__init__(self, parent, id, title, pos, size, style)

		#--------------------------------------------------------------
		self.toggles_ids= [ID_IP_POOL, ID_IP_TEST]
		if utils.isWin32():
			self._tbIcon = trayicon.TrayIcon(self, images.logo48.Icon)
		self._panel = wx.Panel(self)
		self._ribbon = RB.RibbonBar(self._panel, style=RB.RIBBON_BAR_DEFAULT_STYLE | RB.RIBBON_BAR_SHOW_PANEL_EXT_BUTTONS)

		rb_page = RB.RibbonPage(self._ribbon, wx.ID_ANY, 'IP代理地址池')

		ip_panel = RB.RibbonPanel(rb_page, wx.ID_ANY, 'IP工具', style=RB.RIBBON_PANEL_NO_AUTO_MINIMISE | RB.RIBBON_PANEL_EXT_BUTTON)
		ip_bar = RB.RibbonButtonBar(ip_panel, wx.ID_ANY)
		ip_bar.AddToggleButton(ID_IP_POOL, 'IP代理爬取', images.pool.Bitmap)
		ip_bar.AddToggleButton(ID_IP_TEST, 'IP代理测试', images.test.Bitmap)

		setting_panel = RB.RibbonPanel(rb_page, wx.ID_ANY, '设置')
		setting_bar = RB.RibbonButtonBar(setting_panel, wx.ID_ANY)
		setting_bar.AddButton(ID_IP_SETTING, '设置', images.setting.Bitmap)

		self._ribbon.Realize()

		#--------------------------------------------------------------
		self.poolpanel = PoolPanel(self._panel, wx.ID_ANY)
		self.proxyspider = ProxySpider(wx.GetApp().cfg_path)
		#--------------------------------------------------------------

		s = wx.BoxSizer(wx.VERTICAL)
		s.Add(self._ribbon, 0, wx.EXPAND)
		s.Add(self.poolpanel, 1, wx.EXPAND)
		self._panel.SetSizer(s)

		self.BindEvents([ip_bar])
		self.SetIcon(images.logo48.Icon)
		self.CenterOnScreen()
		self.setArtProvider(RB.RibbonMSWArtProvider())
		#self.refresh(self)

	def BindEvents(self, bars):
		# bar0, bar1 = bars
		# toggle toolbar click
		for btn_id in self.toggles_ids:
			self.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onToogleClick, id=btn_id)
		
		#self.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.poolpanel.statpanel.onAddRow, id=ID_IP_SETTING)
		self.Bind(RB.EVT_RIBBONBUTTONBAR_CLICKED, self.onSettingClick, id=ID_IP_SETTING)

		if utils.isWin32():
			self.Bind(wx.EVT_ICONIZE, self.onIconify)
		self.Bind(wx.EVT_CLOSE, self.onClose)

	def onToogleClick(self, event):
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
	
	def onSettingClick(self, event):
		dlg = SettingDialog(self, -1, '配置', size=(350, 200))
		dlg.ShowWindowModal()

	def onIconify(self, event):
		self.Hide()

	def onClose(self, event):
		'''
		Destroy the taskbar icon and the frame
		'''
		if utils.isWin32():
			self._tbIcon.RemoveIcon()
			self._tbIcon.Destroy()
		self.Destroy()

	def setArtProvider(self, prov):
		self._ribbon.DismissExpandedPanel()
		self._ribbon.Freeze()
		self._ribbon.SetArtProvider(prov)
		self._ribbon.Thaw()
		self._ribbon.Realize()
	
	# def refresh_full(self, sender):
	# 	self.poolpanel.refresh()

	# def refresh(self, sender):
	# 	self.poolpanel.refresh_led()