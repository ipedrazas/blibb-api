from flask import Blueprint, request, abort, jsonify, g, current_app, render_template
from API.oiapp.models import User, Audit, Oi
from API.decorators import crossdomain
from API.decorators import support_jsonp
from API.oiapp.models import AcraError
from datetime import datetime



webtool = Blueprint('oiwebtool', __name__, url_prefix='/tools')


@webtool.route('/acra', methods=['POST'])
@crossdomain(origin='*')
def new_acra_error_msg():
    acra = {
        'timestamp':  datetime.now(),
        'stack_trace': request.form.get('STACK_TRACE',''),
        'package_name': request.form.get('PACKAGE_NAME',''),
        'app_version_code': request.form.get('APP_VERSION_CODE',''),
        'app_version_name': request.form.get('APP_VERSION_NAME',''),
        'phone_model': request.form.get('PHONE_MODEL',''),
        'android_version': request.form.get('ANDROID_VERSION',''),
        'display': request.form.get('DISPLAY',''),
        'installation_id': request.form.get('INSTALLATION_ID',''),
    }
    AcraError.add(acra)
    return "ok"


