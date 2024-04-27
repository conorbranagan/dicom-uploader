import pytest

from dicom_upload import create_app
from dicom_upload.models import db


@pytest.fixture()
def testapp(request):
    app = create_app('dicom_upload.settings.TestConfig', env='dev')
    with app.app_context():
        client = app.test_client()

        db.create_all()

        def teardown():
            with app.app_context():
                db.session.remove()
                db.drop_all()

        request.addfinalizer(teardown)

    return client
