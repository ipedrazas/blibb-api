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
    current_app.logger.info(str(request.form))
    acra = {
        'timestamp':  datetime.now(),
        'stack_trace': request.form['stack_trace'],
        'package_name': request.form['package_name'],
        'app_version_code': request.form['app_version_code'],
        'app_version_name': request.form['app_version_name'],
        'phone_model': request.form['phone_model'],
        'android_version': request.form['android_version'],
        'display': request.form['display'],
        'installation_id': request.form['installation_id']
    }
    current_app.logger.info(str(acra))
    AcraError.add(acra)
    return "ok"
