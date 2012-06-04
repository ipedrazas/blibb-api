
from API.om.manager import Manager
from API.event.event import Event
import API.utils as utils

from flask import Blueprint, request, redirect, abort, current_app, jsonify
from functools import wraps
import json


mod = Blueprint('manager', __name__, url_prefix='/sys')


@mod.route('/hi')
def hello_world():
	return "Hello World, this is Manager'"
