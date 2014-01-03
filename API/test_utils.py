# test_utils.py


from utils import queue_bookmarks


oid = '522ee71b56c02c0580abe64d'
owner = 'ivan'
url = 'http://docs.vagrantup.com'


res = queue_bookmarks(oid, url, owner)
print str(res)
