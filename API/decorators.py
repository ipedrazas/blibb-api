

from datetime import timedelta
from flask import make_response, request, current_app, abort
from functools import update_wrapper
from functools import wraps


def parse_args(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        params = request.args.get('fields')
        page = request.args.get('page', 1)
        num = request.args.get('num', 20)
        items = request.args.get('items')
        raw_filters = request.args.get('filter')
        fields = dict()
        filters = dict()
        if filters:
            for filt in raw_filters.split(','):
                entry = filt.split(':')
                filters[entry[0].strip()] = entry[1].strip()
        if params:
            for p in params.split(','):
                fields[p.strip()] = 1
        kwargs.update({'page': page, 'num': num, 'items': items, 'fields': fields, 'filters': filters})
        return f(*args, **kwargs)
    return decorator


def check_tokens(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        app_token = request.args.get('app_token', False)
        user_token = request.args.get('user_token', False)
        if app_token or user_token:
            pass
        else:
            abort(401)
    return decorated_function


def support_jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f(*args, **kwargs).data) + ')'
            return current_app.response_class(content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)
    return decorated_function


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)

            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator







