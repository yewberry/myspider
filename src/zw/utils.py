import time
import sys

class Timeit:
	def __init__(self):
		self.ts = time.time()
	
	def start(self):
		self.ts = time.time()
	
	def end(self):
		te = time.time()
		secs = te - self.ts
		msecs = secs * 1000
		return msecs

def isMacOS():
	return True if sys.platform == 'darwin' else False

def isWin32():
	return True if sys.platform == 'win32' else False