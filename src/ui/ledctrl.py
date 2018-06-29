import wx
import wx.lib.gizmos as gizmos

class LEDCtrl(gizmos.LEDNumberCtrl):
	def __init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize
				, style=gizmos.LED_ALIGN_CENTER|gizmos.LED_DRAW_FADED, fgcolor='green'):
		gizmos.LEDNumberCtrl.__init__(self, parent, id, pos, size, style)
		self.SetForegroundColour(fgcolor)
		self.SetValue('0')
		self.values = []


