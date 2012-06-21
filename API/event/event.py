# 
#
#	event.py
#
#


from datetime import datetime
from pymongo import Connection

class Event(object):

	def __init__(self, eventName=None):
		self._db = 'logging'
		self._collection = 'events'
		self._conn = Connection()
		self._db = self._conn[self._db]
		self._objects = self._db[self._collection]
		self._log = []
		if eventName is not None:
			self._name = eventName
		self._start = datetime.utcnow()
		

	def addLog(self, log):
		self._log.append(log)

	def save(self,dates=False):
		self._end = datetime.utcnow()
		self._duration = self._end - self._start
		self.toDB()
		
	def toDB(self):
		doc = {"d" : self._duration.microseconds, "c": self._start, "l": self._log, "n": self._name}
		newId = self._objects.insert(doc)
		return str(newId)

	def getEventLog(self):
		return ' '.join(self._log)

	

	#
	#	MapReduce to get the Average times of events:
	#	Results are in microseconds: yes, a microsecond is 0.000001 s
	#

		# m1 = function(){ 
		# 	var microseconds = parseInt(this.d.substring(9));
		# 	emit(this.n, microseconds);			
		# }

		# r3 = function(doc, values){ 
		#               var c = 0;
		#               var ssum = 0; 
		#               values.forEach(
		#                 function(f) { 
		#                   ssum += f; 
		#                   c++;
		#                 }); 
		#               return ssum/c;
		#       };

		# res = db.events.mapReduce(m1, r3, {out: 'medias'});

