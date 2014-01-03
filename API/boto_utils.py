## boto_utils.py

from boto import connect_s3
from boto.s3.key import Key

from API.utils import get_config_value

def upload_image_as_png_to_s3(filename, user):
    c = connect_s3()
    bucket_name = get_config_value('BUCKET')
    bucket = c.create_bucket(bucket_name)
    k = Key(bucket)
    k.key = user + '/' + filename
    k.set_metadata('owner', user)
    k.content_type = 'image/png'
    k.set_contents_from_filename(filename)
    k.make_public()
    return 'http://%s/%s' % (bucket_name, k.key)


