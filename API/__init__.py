###


from flask import Flask, render_template
import os
import logging

app = Flask(__name__)


if not app.debug:
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)


# Config
if os.path.exists('/var/blibb/dev.pid'):
    app.config.from_object('API.config.DevelopmentConfig')
    app.logger.info("Config: Development")
    app.logger.setLevel(logging.DEBUG)
    lvl = logging.getLevelName(app.logger.getEffectiveLevel())
    app.logger.info("LogLevel " + lvl)
elif os.path.exists('/var/blibb/test.pid'):
    app.config.from_object('API.config.TestConfig')
    app.logger.info("Config: Test")
    lvl = logging.getLevelName(app.logger.getEffectiveLevel())
    app.logger.info("LogLevel " + lvl)
else:
    app.config.from_object('API.config.ProductionConfig')
    app.logger.info("Config: Production")
    lvl = logging.getLevelName(app.logger.getEffectiveLevel())
    app.logger.info("LogLevel " + lvl)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


from API.web.wmanager import mod as ManagerModule
from API.blibb.weblibb import mod as BlibbModule
from API.blitem.weblitem import mod as BlitemModule
from API.contenttypes.webcontent import mod as ContentModule
from API.control.webcontrol import mod as ControlModule
from API.template.webtemplate import template as TemplateModule
from API.user.webuser import mod as UserModule
from API.comment.webcomment import mod as CommentModule
from API.oiapp.weboi import oi as OiModule
from API.oiapp.webuser import oiuser as UserOiModule
from API.oiapp.webtool import webtool as WebOiModule
from API.bsm.webbsm import bsm as WebBsmModule


app.register_blueprint(WebBsmModule)
app.register_blueprint(WebOiModule)
app.register_blueprint(UserOiModule)
app.register_blueprint(OiModule)
app.register_blueprint(CommentModule)
app.register_blueprint(BlibbModule)
app.register_blueprint(BlitemModule)
app.register_blueprint(ContentModule)
app.register_blueprint(ControlModule)
app.register_blueprint(TemplateModule)
app.register_blueprint(UserModule)
app.register_blueprint(ManagerModule)
