import storm.locals

class FileDatabase(storm.locals.Store):
	__V1 = """
		CREATE TABLE SyncedFile (
			ID INTEGER PRIMARY KEY AUTOINCREMENT,
			remoteID INTEGER,
			fileURI VARCHAR(512) UNIQUE NOT NULL
		);

		CREATE TABLE SyncedFileTag (
			fileID INTEGER NOT NULL,
			tag VARCHAR(512) NOT NULL,
			status INTEGER(1), --  0 = new, 1 = synced, 2 = deleted
			UNIQUE (fileID, tag),
			FOREIGN KEY (fileID) REFERENCES SyncedFile(ID)
		);
	"""
	versions = (__V1, )
	latest_version = len(versions)
	
	def __init__(self, fileName):
		storm.locals.Store.__init__(self, storm.locals.create_database('sqlite:///' + fileName))
	
	def updateTo(self, current):
		if current == None:
			current = -1
		for update in xrange(current + 1, FileDatabase.latest_version):
			queries = FileDatabase.versions[update].split("\n\n")
			for q in queries:
				self.execute(q)
		
		return FileDatabase.latest_version
