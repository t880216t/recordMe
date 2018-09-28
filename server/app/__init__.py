from flask import Flask

app = Flask(__name__)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif','HTML','html','xlsx'])

from app import task
from app import views
from app import car
from app import hzw
from app import record