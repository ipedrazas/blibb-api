


errors = {
	
	'id_not_valid': 'Object id not valid'
}

class Message(object):
	
	@classmethod
	def getMessage(self, key):
		return errors[key]

	@classmethod
	def get(self, key):
		return {'error': errors[key]}
