



import boto
from boto.s3.key import Key

c = boto.connect_s3()
b = c.create_bucket('dev.blibb')
k = Key(b)
k.key = 'myfile'
k.set_metadata('meta1', 'This is the first metadata value')
k.set_contents_from_filename('/home/ivan/Downloads/zendesk.png')
