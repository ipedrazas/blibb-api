###


from flask import Flask, render_template


app = Flask(__name__)
app.config.from_object('config')


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404




from API.web.wmanager import mod as ManagerModule
from API.blibb.weblibb import mod as BlibbModule
from API.blitem.weblitem import mod as BlitemModule
from API.contenttypes.webcontent import mod as ContentModule
from API.control.webcontrol import mod as ControlModule
from API.template.webtemplate import mod as TemplateModule
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