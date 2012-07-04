#
#
#
#

class ACL(object):

	ONLY_ME = 1
	GROUP = 5
	EVERYBODY = 11

	level = {'1': 'Only me', '5': 'Group', '11': 'Everybody'}

	@classmethod
	def get_access(self, level):
		return self.level.get(level)
