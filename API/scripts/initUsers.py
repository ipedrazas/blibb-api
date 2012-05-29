

###
###
###		User Unit Test
###
###
###

import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)



from API.user.buser import User



def createInitialBatch():
	createUser('test','test','test')
	createUser('alpheta','alpheta@blibb.net','alpheta')
	createUser('ipedrazas','ipedrazas@gmail.com','ivan')
	createUser('manu','mquintans@gmail.com','manu')
	createUser('valgreens','avalverde@blibb.net','antonio')
	createUser('franziska','franziska.london@gmail.com','franziska')



def createUser(name, email, password):
	user = User()
	user.name = name
	user.email = email
	user.password = password
	user.active = True

	return user.save()


createInitialBatch()