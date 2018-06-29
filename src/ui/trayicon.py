import wx
from wx.adv import TaskBarIcon

'''
in frame:
if utils.isWin32():
	self.Bind(wx.EVT_ICONIZE, self.onIconify)
self.Bind(wx.EVT_CLOSE, self.onClose)

def onIconify(self, event):
	self.Hide()
def onClose(self, event):
	if utils.isWin32():
		self._tbIcon.RemoveIcon()
		self._tbIcon.Destroy()
	self.Destroy()
'''
class TrayIcon(TaskBarIcon):
	def __init__(self, frame, ico, tooltip='Restore'):
		"""Constructor"""
		TaskBarIcon.__init__(self)
		self.frame = frame
 
		self.SetIcon(ico, tooltip)
		self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.onTaskBarLeftClick)
		self.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN, self.onTaskBarRightClick)
 
	def onTaskBarRightClick(self, evt):
		pass
 
	def onTaskBarLeftClick(self, evt):
		if self.frame.IsIconized():
			self.frame.Iconize(False)
		if not self.frame.IsShown():
			self.frame.Show(True)
			self.frame.Raise()
