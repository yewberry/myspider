import wx
import wx.dataview as dv
from blinker import signal

import zw.images as images
from zw.database import Database

class StatPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)
		self.init_ui()
		self.load_data()
		self.bind_event()
	
	def init_ui(self):
		self.dvc = dvc = dv.DataViewCtrl(self,
								   style=wx.BORDER_THEME
								   | dv.DV_ROW_LINES # nice alternating bg colors
								   #| dv.DV_HORIZ_RULES
								   | dv.DV_VERT_RULES
								   | dv.DV_MULTIPLE
								   )

		dvc.AppendIconTextColumn('国家', 0, width=40)
		dvc.AppendTextColumn("IP地址", 1, width=120)
		dvc.AppendTextColumn("端口", 2, width=50)
		dvc.AppendTextColumn('服务器地址', 3, width=100)
		dvc.AppendProgressColumn('速度', 4, width=100)
		dvc.AppendTextColumn('连接类型', 5, width=80)
		dvc.SetIndent(0)
		for c in dvc.Columns:
			c.Sortable = True
			c.Reorderable = True
			c.MinWidth = 40
			# c.Alignment = wx.ALIGN_CENTER
			# c.Renderer.Alignment = wx.ALIGN_CENTER
		self.Sizer = wx.BoxSizer(wx.VERTICAL)
		self.Sizer.Add(dvc, 1, wx.EXPAND)
	
	def load_data(self):
		rows = self.getall()
		self.model = StatListModel(rows)
		# Tel the DVC to use the model
		self.dvc.AssociateModel(self.model)
	
	def bind_event(self):
		sig_refresh = signal('refresh')
		sig_refresh.connect(self.refresh)

	def onDeleteRows(self, evt):
		# Remove the selected row(s) from the model. The model will take care
		# of notifying the view (and any other observers) that the change has
		# happened.
		items = self.dvc.GetSelections()
		rows = [self.model.GetRow(item) for item in items]
		self.model.DeleteRows(rows)
	
	def refresh(self, sender=None):
		dat = self.getall()
		# called by thread signal, must use CallAfter to invoke in main thread
		wx.CallAfter(self.model.add_update_rows, dat)
	
	def getall(self):
		db = Database()
		rows = db.query('ippool_all')
		rows = rows.as_dict()
		if len(rows) == 0:
			return []
		delt = rows[len(rows)-1]['speed'] - rows[0]['speed']
		rows = [ [d['country'],d['ip'],d['port'],d['city'], 100-int( 100*(d['speed']/delt) ), d['conn_type']] for d in rows]
		return rows

class StatListModel(dv.DataViewIndexListModel):
	def __init__(self, data):
		dv.DataViewIndexListModel.__init__(self, len(data))
		self.data = data
		self.dmap = {}
		for idx, d in enumerate(data):
			self.dmap[self.get_key(d)] = idx
		
	def GetColumnType(self, col):
		'''
		string bool datetime
		'''
		return 'string'

	def GetValueByRow(self, row, col):
		if col == 0:
			return wx.dataview.DataViewIconText(text="", icon=images.flag_cn.Icon)
		else:
			return self.data[row][col]
	
	def GetColumnCount(self):
		return len(self.data[0])
	
	def GetCount(self):
		return len(self.data)
		
	def GetAttrByRow(self, row, col, attr):
		# if col == 3:
		# 	attr.SetColour('blue')
		# 	attr.SetBold(True)
		# 	return True
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
	
	def DeleteRows(self, rows):
		# make a copy since we'll be sorting(mutating) the list
		rows = list(rows)
		# use reverse order so the indexes don't change as we remove items
		rows.sort(reverse=True)
		
		for row in rows:
			# remove it from our data structure
			del self.data[row]
			# notify the view(s) using this model that it has been removed
			self.RowDeleted(row)
			
	def AddRow(self, value):
		# update data structure
		self.data.append(value)
		# notify views
		self.RowAppended()
	
	def get_key(self, d):
		return '%s_%s' % (d[1], d[2])

	def get_index(self, d):
		k = self.get_key(d)
		return self.dmap[k] if k in self.dmap else -1

	def isdirty(self, d):
		idx = self.get_index(d)
		if idx > -1:
			o = self.data[idx]
			for i, p in enumerate(o):
				if p != d[i]:
					return True, idx
		return False, idx
	
	def isnew(self, d):
		idx = self.get_index(d)
		return idx == -1
	
	def add_update_rows(self, dat):
		for d in dat:
			r, idx = self.isdirty(d)
			if r:
				self.data[idx] = d
				self.RowChanged(idx)

			if self.isnew(d):
				self.data.append(d)
				self.RowAppended()
		


