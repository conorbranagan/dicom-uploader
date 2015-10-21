# stdlib
import io
import os.path

# 3p
from flask import json
import pytest
import nose.tools as nt


@pytest.mark.usefixtures("testapp")
class TestAPI(object):
    def _test_data_path(self, file_id):
        data_path = os.path.join(os.path.dirname(__file__), 'test_data')
        return os.path.join(data_path, 'test_%s.dcm' % file_id)

    def test_index(self, testapp):
        """ Tests that the index page loads """
        res = testapp.get('/')
        nt.eq_(res.status_code, 200)

    def test_api(self, testapp):
        """ Verify that we can send files and they are persisted. """
        dicom_ids = []

        # Test single file upload.
        res = testapp.post('/dicom', data={
            'file1': (open(self._test_data_path(1), 'rb'), 'test_1.dcm')
        })
        nt.eq_(res.status_code, 200)
        res_data = json.loads(res.data)
        assert 'dicom_files' in res_data
        nt.eq_(len(res_data['dicom_files']), 1)
        dicom_ids.append(res_data['dicom_files'][0]['id'])

        # Test multi file upload.
        res = testapp.post('/dicom', data={
            'file1': (open(self._test_data_path(2), 'rb'), 'test_2.dcm'),
            'file2': (open(self._test_data_path(3), 'rb'), 'test_3.dcm'),
        })
        nt.eq_(res.status_code, 200)
        res_data = json.loads(res.data)
        assert 'dicom_files' in res_data
        nt.eq_(len(res_data['dicom_files']), 2)
        dicom_ids.append(res_data['dicom_files'][0]['id'])
        dicom_ids.append(res_data['dicom_files'][1]['id'])

        # Verify that everything is persisted.
        res = testapp.get('/dicom')
        nt.eq_(res.status_code, 200)
        res_data = json.loads(res.data)
        assert 'dicom_files' in res_data
        nt.eq_(len(res_data['dicom_files']), 3)
        res_ids = [df['id'] for df in res_data['dicom_files']]
        nt.eq_(res_ids, dicom_ids)

        # Make sure getting a single file works too.
        res = testapp.get('/dicom/%s' % dicom_ids[0])
        nt.eq_(res.status_code, 200)
        res_data = json.loads(res.data)
        nt.eq_(res_data['id'], dicom_ids[0])

        # Verify file deletion.
        for dicom_id in dicom_ids:
            res = testapp.delete('/dicom/%s' % dicom_id)
            nt.eq_(res.status_code, 204)
        res = testapp.get('/dicom')
        nt.eq_(res.status_code, 200)
        res_data = json.loads(res.data)
        assert 'dicom_files' in res_data
        nt.eq_(len(res_data['dicom_files']), 0)

    def test_api_errors(self, testapp):
        """ Make sure our API endpoints handle errors cleanly (no 500s!) """
        res = testapp.post('/dicom', data={
            'file1': (io.BytesIO(b'blah blah'), 'invalid.dcm')
        })
        nt.eq_(res.status_code, 400)
        res_data = json.loads(res.data)
        assert 'error' in res_data, res_data

        res = testapp.get('/dicom/123456')
        nt.eq_(res.status_code, 404)
        res_data = json.loads(res.data)
        assert 'error' in res_data, res_data

    def test_annotate(self, testapp):
        """ Test that we can annotate dicom files. """
        res = testapp.post('/dicom', data={
            'file1': (open(self._test_data_path(1), 'rb'), 'test_1.dcm')
        })
        nt.eq_(res.status_code, 200)
        res_data = json.loads(res.data)
        assert 'dicom_files' in res_data
        nt.eq_(len(res_data['dicom_files']), 1)
        dicom_id = res_data['dicom_files'][0]['id']

        annotation = 'This is an annotation'
        res = testapp.post('/dicom/annotate/%s' % dicom_id, data={
            'annotation': annotation
        })
        nt.eq_(res.status_code, 200)
        res_data = json.loads(res.data)
        nt.eq_(res_data['id'], dicom_id)
        nt.eq_(res_data['annotation'], annotation)
