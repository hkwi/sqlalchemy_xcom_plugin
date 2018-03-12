import socket
import warnings
import sqlalchemy.engine
import sqlalchemy.event
import sqlalchemy.exc

class XcomPlugin(sqlalchemy.engine.CreateEnginePlugin):
	def __init__(self, url, *args, **kwargs):
		self.url = url

	def engine_created(self, en):
		if en.dialect.name != "mysql":
			return
		sqlalchemy.event.listen(en, "do_connect", do_connect)

	def handle_pool_kwargs(self, pool_cls, pool_args):
		dialect = pool_args.get("dialect")
		if dialect and dialect.name == "mysql":
			sqlalchemy.event.listen(pool_cls, "checkout", pre_ping)


def super_read_only(db):
	with db.cursor() as cur:
		assert 1==cur.execute("SELECT @@super_read_only")
		return 1==cur.fetchone()[0]

def pre_ping(con, connection_record, proxy):
	try:
		ro = super_read_only(con)
	except:
		raise sqlalchemy.exc.InvalidatePoolError("query super_read_only failed")
	
	if ro:
		raise sqlalchemy.exc.InvalidatePoolError("invalidate by super_read_only")

def do_connect(dialect, connection_record, cargs, cparams):
	if dialect.name != "mysql":
		return

	con = dialect.connect(*cargs, **cparams)
	if not super_read_only(con):
		return con
	
	primary = None
	try:
		cur = con.cursor()
		rows = cur.execute('''SELECT MEMBER_HOST,MEMBER_PORT
				FROM performance_schema.replication_group_members
				WHERE MEMBER_ID=(SELECT VARIABLE_VALUE 
					FROM performance_schema.global_status
					WHERE VARIABLE_NAME=%s)''',
			("group_replication_primary_member",))
		if rows:
			primary = cur.fetchone()
		cur.close()
	except:
		warnings.warn("query performance_schema failed")
	
	con.close()
	
	# Try basic DNS round-robin first
	host = cparams.get("host", "localhost")
	port = cparams.get("port", 3306)
	addrs = set([i[4][:2] for i in socket.getaddrinfo(host, port,
		type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)])
	if len(addrs) > 1:
		for addr in addrs:
			np = dict(cparams)
			np.update(host=addr[0], port=addr[1])
			con = dialect.connect(*cargs, **np)
			if not super_read_only(con):
				return con
			con.close()
	
	# If report-host was properly configured, following may work
	if primary:
		cparams["host"] = primary[0]
		cparams["port"] = primary[1]
	return dialect.connect(*cargs, **cparams)


