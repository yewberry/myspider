import records

import zw.logger as logger

LOG = logger.getLogger(__name__)
class Database():
	DB_INIT_SQL = {
		'sqlite': [
			"""CREATE TABLE IF NOT EXISTS ippool (id INTEGER PRIMARY KEY AUTOINCREMENT
				, ip TEXT, port TEXT, country TEXT, city TEXT, speed FLOAT, valid INT DEFAULT 0
				, conn_type TEXT, update_time TIMESTAMP NOT NULL DEFAULT 
				(datetime(CURRENT_TIMESTAMP,'localtime')) )"""
			, """CREATE TRIGGER IF NOT EXISTS update_timestamp AFTER UPDATE ON ippool 
				FOR EACH ROW WHEN NEW.update_time < datetime(CURRENT_TIMESTAMP,'localtime') 
				BEGIN UPDATE ippool SET update_time=datetime(CURRENT_TIMESTAMP,'localtime') WHERE id=OLD.id; END;"""
		]
		, 'mysql': [
			"""CREATE TABLE IF NOT EXISTS ippool (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT
				, ip TEXT, port TEXT, country TEXT, city TEXT, speed FLOAT, valid INT DEFAULT 0
				, conn_type TEXT, update_time TIMESTAMP NOT NULL DEFAULT 
				CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)"""
		]
	}
	DB_SQL = {
		'ippool_all': 'SELECT * FROM ippool ORDER BY speed ASC'
		, 'ippool_count': 'SELECT count(*) as c, sum(case when valid=1 then 1 else 0 end) as s, sum(case when valid=0 then 1 else 0 end) as f FROM ippool'
		, 'ippool_exist': 'SELECT count(*) AS c FROM ippool WHERE ip=:ip AND port=:port'
		, 'ippool_insert': 'INSERT INTO ippool (ip, port, country, city, speed, conn_type) VALUES(:ip, :port, :country, :city, :speed, :conn_type)'
		, 'ippool_update': 'UPDATE ippool SET country=:country, city=:city, speed=:speed, conn_type=:conn_type WHERE ip=:ip AND port=:port'
		, 'ippool_update_valid': 'UPDATE ippool SET valid=:valid WHERE ip=:ip AND port=:port'
	}
	DB_CFG_DEF = None
	def __init__(self, o=None, set_cfg_def=True):
		o = Database.DB_CFG_DEF if o is None else o
		self.db_cfg = o
		self.dbtype = o['dbtype']
		self.dbname = o['dbname']
		self.dbuser = o['dbuser']
		self.dbpass = o['dbpass']
		self.dbaddr = o['dbaddr']
		self.db = None
		Database.DB_CFG_DEF = o if set_cfg_def else Database.DB_CFG_DEF
	
	def init_db(self):
		if self.db is not None:
			self.close()
		self.db = db = self.get_db()
		sqls = Database.DB_INIT_SQL[self.dbtype]
		for sql in sqls:
			#LOG.debug(sql)
			t = db.transaction()
			db.query(sql)
			t.commit()
	
	def get_db(self):
		if self.db is None:
			if 'sqlite' == self.dbtype:
				db = records.Database('sqlite:///%s' % self.dbname)
			elif 'mysql' == self.dbtype:
				db = records.Database('mysql+pymysql://%s:%s@%s/%s?charset=utf8' % (self.dbuser, self.dbpass, self.dbaddr, self.dbname))
			self.db = db
		return self.db
	
	def query(self, op, **params):
		sql = Database.DB_SQL[op]
		db = self.get_db()
		# LOG.debug(sql)
		rows = db.query(sql, **params)
		return rows
	
	def bulk_query(self, op, *multiparams):
		sql = Database.DB_SQL[op]
		db = self.get_db()
		# LOG.debug(sql)
		rows = db.bulk_query(sql, *multiparams)
		return rows
	
	def insert_update(self, recs, checkop, insertop, updateop, checkflds):
		db = self.get_db()
		recs_insert = []
		recs_update = []
		for r in recs:
			flds = {}
			for f in checkflds:
				flds[f] = r[f]
			rs = db.query(Database.DB_SQL[checkop], **flds)
			if rs[0].c == 0:
				recs_insert.append(r)
			else:
				recs_update.append(r)
		LOG.debug( 'Insert: %s, Update: %s' %(len(recs_insert), len(recs_update)) )
		if len(recs_insert)>0:
			db.bulk_query(Database.DB_SQL[insertop], *recs_insert)
		if len(recs_update)>0:
			db.bulk_query(Database.DB_SQL[updateop], *recs_update)
		return len(recs_insert), len(recs_update)
	
	def close(self):
		self.db.close()
		self.db = None
