import os
import sys
import time
import multiprocessing
import json
from blinker import signal
import shapefile

if __name__ == '__main__':
	sys.path.insert(0, os.path.dirname(sys.path[0]))

from zw.database import Database
import zw.logger as logger

SIG_REFRESH = signal('refresh')
LOG = logger.getLogger(__name__)
class ShpFile():
	def __init__(self, shp_file, out_file, var_name):
		self._shp_file = shp_file
		self._out_file = out_file
		self._var_name = var_name
		if not os.path.isfile(self._shp_file):
			LOG.error('%s file not exists!' % os.path.abspath(self._shp_file))

		reader = shapefile.Reader(self._shp_file)
		fields = reader.fields[1:]
		field_names = [field[0] for field in fields]
		buffer = []
		for idx,sr in enumerate(reader.shapeRecords()):
			atr = dict(zip(field_names, sr.record))
			geom = sr.shape.__geo_interface__
			coord = geom['coordinates']
				
			buffer.append(dict(type="Feature", geometry=geom, properties=atr))

		with open(self._out_file, 'w') as f:
			f.write('cnfic = cnfic?cnfic:{};\n')
			d = {"type": "FeatureCollection","features": buffer}
			s = json.dumps(d, cls=MyEncoder) + '\n'
			f.write( 'cnfic.%s=%s\n' % (self._var_name, s) )

class MyEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, bytes):
			return str(obj, encoding='gbk');
		return json.JSONEncoder.default(self, obj)

if __name__ == '__main__':
	p = ShpFile('./etc/shapefiles/省级_region.shp', './etc/prov_data.js', 'provPg')
	# p = MyShapeReader('./etc/shapefiles/县级_region.shp')

