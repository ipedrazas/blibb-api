

import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

import yourls.client

c = yourls.client.YourlsClient('http://ccs.im/yourls-api.php', username='blb', password='blb')
url = c.shorten('http://www.yelp.com/123', custom='something')
print url