###


from flask import Flask, render_template
import os

app = Flask(__name__)


# Config
if os.getenv('DEV') == 'yes':
    app.config.from_object('API.config.DevelopmentConfig')
    app.logger.info("Config: Development")
elif os.getenv('TEST') == 'yes':
    app.config.from_object('API.config.TestConfig')
    app.logger.info("Config: Test")
else:
    app.config.from_object('API.config.ProductionConfig')
    app.logger.info("Config: Production")

# Logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s', datefmt='%Y%m%d-%H:%M%p',
)


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


app.register_blueprint(CommentModule)
app.register_blueprint(BlibbModule)
app.register_blueprint(BlitemModule)
app.register_blueprint(ContentModule)
app.register_blueprint(ControlModule)
app.register_blueprint(TemplateModule)
app.register_blueprint(UserModule)
app.register_blueprint(ManagerModule)
