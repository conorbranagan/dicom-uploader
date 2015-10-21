# stdlib
from datetime import date
import os
import uuid

# 3p
import dicom
from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy

# project
from dicom_upload.lib import dicom as dicom_lib

db = SQLAlchemy()


class DicomParsingException(Exception):
    """ Thrown when a file is unable to be parsed by the dicom library. """
    pass


class DicomPILException(Exception):
    """ Throwing if we're unable to convert a Dicom pixel array to PIL. """
    pass


class DicomFile(db.Model):
    """ A model representation of a dicom file. New file creation should only be
        happen via `from_file` for consistency.
    """
    IMG_FORMAT = 'JPEG'
    MAX_RETRIES = 10

    # Schema
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    annotation = db.Column(db.Text())
    raw_filename = db.Column(db.String(200))
    img_filename = db.Column(db.String(200))
    thumb_filename = db.Column(db.String(200))
    patient_name = db.Column(db.String(200))
    patient_sex = db.Column(db.String(2))
    patient_age = db.Column(db.Integer())
    study_date = db.Column(db.Date())

    @classmethod
    def from_file(cls, filename, fh):
        """ Create a DicomFile from an open file handle. """
        try:
            ds = dicom.read_file(fh)
        except Exception:
            raise DicomParsingException(filename)

        files = cls._write_file(ds, filename)

        # Extract some header data.
        patient_name = str(getattr(ds, 'PatientName', 'Unknown'))
        patient_sex = str(getattr(ds, 'PatientSex', 'NA'))

        try:
            study_date = dicom_lib.parse_date(ds.StudyDate)
        except Exception:
            study_date = None

        try:
            patient_age = dicom_lib.parse_age(ds.PatientAge)
        except Exception:
            patient_age = None

        # Start with an empty annotation.
        annotation = None

        return cls(filename, annotation, files.get('raw'), files.get('img'),
                   files.get('thumb'), patient_name, patient_sex, patient_age,
                   study_date)

    @classmethod
    def _write_file(cls, ds, filename):
        """ Write out the Dicom files to an internal location.
            Could be extended to use S3 or another file store later on.
        """
        if not filename.endswith('.dcm'):
            filename = '%s.dcm' % filename

        # Generate a unique filename to avoid collisions.
        retries = 0
        raw_base_path = current_app.config['DICOM_ABS_UPLOAD_DIR']
        while retries < cls.MAX_RETRIES:
            prefix = str(uuid.uuid4().hex[0:6])
            raw_filename = '%s_%s' % (prefix, filename)
            raw_path = os.path.join(raw_base_path, raw_filename)
            if not os.path.exists(raw_path):
                break
            retries += 1

        if retries > cls.MAX_RETRIES:
            # We didn't get a unique filename?!
            raise Exception("Unable to generate a unique filename after "
                            "%d retries!" % cls.MAX_RETRIES)

        # Write the raw file.
        with open(raw_path, 'wb+') as f:
            dicom.write_file(f, ds)

        # Attempt to convert to an image and write out.
        img_base_path = current_app.config['IMG_ABS_UPLOAD_DIR']
        try:
            img = dicom_lib.pil_from_dataset(ds)
        except Exception:
            # Just move on if we can't get an image.
            return {'raw': raw_filename}

        img_filename = raw_filename.rsplit('.', 1)[0] + '.jpg'
        img_path = os.path.join(img_base_path, img_filename)
        with open(img_path, 'wb+') as f:
            img.save(f, format=cls.IMG_FORMAT)

        # Also save a thumbnail.
        img.thumbnail((64, 64))
        thumb_filename = raw_filename.rsplit('.', 1)[0] + '.thumb.jpg'
        thumb_path = os.path.join(img_base_path, thumb_filename)
        with open(thumb_path, 'wb+') as f:
            img.save(f, format=cls.IMG_FORMAT)

        return {
            'raw': raw_filename,
            'img': img_filename,
            'thumb': thumb_filename,
        }

    def __init__(self, filename, annotation, raw_fn, img_fn, thumb_fn,
                 patient_name, patient_sex, patient_age, study_date):
        self.annotation = annotation
        self.filename = filename
        self.raw_filename = raw_fn
        self.img_filename = img_fn
        self.thumb_filename = thumb_fn
        self.patient_name = patient_name
        self.patient_sex = patient_sex
        self.patient_age = patient_age
        self.study_date = study_date

    def to_json_dict(self):
        if self.thumb_filename:
            thumb_url = os.path.join('/dicom/img/%s' % self.thumb_filename)
            img_url = os.path.join('/dicom/img/%s' % self.img_filename)
        else:
            thumb_url, img_url = None, None

        if self.study_date:
            study_date = date.strftime(self.study_date, '%Y-%m-%d')
        else:
            study_date = None

        return {
            'id': self.id,
            'annotation': self.annotation,
            'filename': self.filename,
            'raw_url': os.path.join('/dicom/raw/%s' % self.raw_filename),
            'thumb_url': thumb_url,
            'img_url': img_url,
            'patient': {
                'name': self.patient_name,
                'sex': self.patient_sex,
                'age': self.patient_age
            },
            'study_date': study_date
        }

    def purge_files(self):
        """ Purge static files from the disk. """
        img_base_path = current_app.config['IMG_ABS_UPLOAD_DIR']
        raw_base_path = current_app.config['DICOM_ABS_UPLOAD_DIR']

        if self.thumb_filename:
            thumb_path = os.path.join(img_base_path, self.thumb_filename)
            os.remove(thumb_path)
        if self.img_filename:
            img_path = os.path.join(img_base_path, self.img_filename)
            os.remove(img_path)
        if self.raw_filename:
            raw_path = os.path.join(raw_base_path, self.raw_filename)
            os.remove(raw_path)
