#
#
#   oimodels.py
#
#

from datetime import datetime
from bson.objectid import ObjectId


class Base(object):

    @classmethod
    def count(cls, *args, **kwargs):
        return cls.objects.find(*args, **kwargs).count()

    @classmethod
    def get_paginated(cls, *args, **kwargs):
        if kwargs is not None:
            num = kwargs.get('num', 20)
            page = kwargs.get('page', 1)
            args += ('del', False)
            page = int(page) if page and page > 0 else 1
            num = int(num) if num and int(num) > 0 else 20
            return cls.objects.find(*args, **kwargs).skip(num * (page - 1)).limit(num)
        else:
            return cls.objects.find(*args, **kwargs)

    @classmethod
    def get_all(cls, *args, **kwargs):
        return cls.get_paginated(*args, **kwargs)

    @classmethod
    def get(cls, *args, **kwargs):
        args += ('del', False)
        return cls.objects.find_one(*args, **kwargs)

    @classmethod
    def get_as_dict(cls, *args, **kwargs):
        args += ('del', False)
        return cls.objects.find_one(*args, **kwargs)

    @classmethod
    def to_dict(cls, obj):
        if obj is not None and not isinstance(obj, unicode) and not isinstance(obj, str):
            for key, value in obj.items():
                if isinstance(value, ObjectId):
                    obj[key] = unicode(value)
                elif isinstance(value, datetime):
                    obj[key] = value.strftime("%d/%m/%Y %H:%M:%S %Z")
                elif isinstance(value, (dict)):
                    obj[key] = cls.to_dict(value)
                elif isinstance(value, (list)):
                    t = []
                    for elem in value:
                        t.append(cls.to_dict(elem))
                    obj[key] = t
                else:
                    obj[key] = value
        return obj

    @classmethod
    def save(cls, object):
        return cls.objects.save(object)


