# -*- coding: utf-8 -*-
import os
import json

class Config():
	def __init__(self, file_path, cfg_default=None):
		self.path = file_path if file_path is not None else './config.json'
		self.data = cfg_default if cfg_default is not None else {}
		if not os.path.isfile(self.path):
			with open(self.path, 'w') as f:
				json.dump(self.data, f, sort_keys=True, indent=4, separators=(',', ': '))
		with open(self.path, 'r') as f:
			self.data = json.load(f)

	def load(self):
		with open(self.path, 'r') as f:
			self.data = json.load(f)
		return self.data

	def save(self):
		with open(self.path, 'w') as f:
			json.dump(self.data, f, sort_keys=True, indent=4, separators=(',', ': '))

