#!/usr/bin/env python

# stdlib
import os

# 3p
from flask.ext.script import Manager, Server
from flask.ext.script.commands import ShowUrls, Clean

# project
from dicom_upload import create_app
from dicom_upload.models import db

env = os.environ.get('APPNAME_ENV', 'dev')
app = create_app('dicom_upload.settings.%sConfig' % env.capitalize(), env=env)

manager = Manager(app)
manager.add_command("server", Server())
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())


@manager.shell
def make_shell_context():
    """ Creates a python REPL with several default imports
        in the context of the app
    """
    return dict(app=app, db=db)


@manager.command
def createdb():
    """ Creates a database with all of the tables defined in
        your SQLAlchemy models
    """
    db.create_all()


if __name__ == "__main__":
    manager.run()
