import sys
import traceback
import multiprocessing
import zw.logger as logger
# must set log file name before any class of my
logger.LOG_FILE = 'myspider.log'

from ui.app import App

LOG = logger.getLogger(__name__)
def main():
	LOG.info('sys.path:'+str(sys.path))
	try:
		LOG.debug('App start...')
		app = App(redirect=False)
		app.SetExitOnFrameDelete(True)
		
		if False:
			import wx.lib.inspection
			wx.lib.inspection.InspectionTool().Show()

		app.MainLoop()
	except Exception as e:
		traceback.print_exc()
		sys.exit(1)

if __name__ == '__main__':
	multiprocessing.freeze_support()
	main()