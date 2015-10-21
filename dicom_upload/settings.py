import os.path
import tempfile

db_file = tempfile.NamedTemporaryFile()
upload_dir = tempfile.mkdtemp()

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
REL_UPLOAD_FOLDER = 'static/uploads'
UPLOAD_FOLDER = os.path.join(APP_ROOT, REL_UPLOAD_FOLDER)


class Config(object):
    SECRET_KEY = '^y\xc4\xc1\x14.\x1c`\xa2e\xee9\xc3\x03]\\\xd0\xf0\xdc\xf1'


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'
    DICOM_ABS_UPLOAD_DIR = os.path.join(UPLOAD_FOLDER, 'dicom')
    DICOM_REL_UPLOAD_DIR = os.path.join('/', REL_UPLOAD_FOLDER, 'dicom')
    IMG_ABS_UPLOAD_DIR = os.path.join(UPLOAD_FOLDER, 'img')
    IMG_REL_UPLOAD_DIR = os.path.join('/', REL_UPLOAD_FOLDER, 'img')


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'
    DICOM_ABS_UPLOAD_DIR = os.path.join(UPLOAD_FOLDER, 'dicom')
    DICOM_REL_UPLOAD_DIR = os.path.join('/', REL_UPLOAD_FOLDER, 'dicom')
    IMG_ABS_UPLOAD_DIR = os.path.join(UPLOAD_FOLDER, 'img')
    IMG_REL_UPLOAD_DIR = os.path.join('/', REL_UPLOAD_FOLDER, 'img')


class TestConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_file.name
    SQLALCHEMY_ECHO = True
    DICOM_ABS_UPLOAD_DIR = upload_dir
    DICOM_REL_UPLOAD_DIR = upload_dir
    IMG_ABS_UPLOAD_DIR = upload_dir
    IMG_REL_UPLOAD_DIR = upload_dir
