# 3p
from flask import Flask

# project
from dicom_upload.controllers.main import main
from dicom_upload.models import db


def create_app(config_obj, env='prod'):
    """ A Flask application factory
            (http://flask.pocoo.org/docs/patterns/appfactories/)
    """
    app = Flask(__name__)

    app.config.from_object(config_obj)
    app.config['ENV'] = env

    db.init_app(app)

    # Register blueprints for the app.
    app.register_blueprint(main)

    return app
