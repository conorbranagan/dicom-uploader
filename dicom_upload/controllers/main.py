# 3p
from flask import Blueprint, current_app, jsonify, render_template, request, \
    send_from_directory

# project
from dicom_upload.models import db, DicomFile, DicomParsingException

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/dicom', methods=['POST'])
def post_dicom():
    try:
        dicom_files = [
            DicomFile.from_file(ufile.filename, ufile.stream)
            for ufile in request.files.values()
        ]
    except DicomParsingException as e:
        error_msg = "{} is an unsupported Dicom file.".format(e)
        content = {'error': error_msg}
        status = 400
    else:
        for df in dicom_files:
            db.session.add(df)
        db.session.commit()

        status = 200
        content = {'dicom_files': [df.to_json_dict() for df in dicom_files]}

    response = jsonify(content)
    response.status_code = status
    return response


@main.route('/dicom/<int:dicom_id>', methods=['DELETE'])
def delete_dicom(dicom_id):
    # Attempt to delete the associated static files.
    df = db.session.query(DicomFile).get(dicom_id)
    if df:
        df.purge_files()

    # Delete from the DB.
    db.session.query(DicomFile).filter(DicomFile.id == dicom_id).delete()
    db.session.commit()
    return ('', 204)


@main.route('/dicom/<int:dicom_id>', methods=['GET'])
def get_dicom(dicom_id):
    df = db.session.query(DicomFile).get(dicom_id)
    if not df:
        status = 404
        content = {'error': 'No dicom file found for id=%s' % dicom_id}
    else:
        status = 200
        content = df.to_json_dict()

    response = jsonify(content)
    response.status_code = status
    return response


@main.route('/dicom', methods=['GET'])
def get_all_dicoms():
    dfs = db.session.query(DicomFile).all()
    return jsonify({'dicom_files': [df.to_json_dict() for df in dfs]})


@main.route('/dicom/annotate/<int:dicom_id>', methods=['POST'])
def annotate_dicom(dicom_id):
    df = db.session.query(DicomFile).get(dicom_id)
    if not df:
        status = 404
        content = {'error': 'No dicom file found for id=%s' % dicom_id}
    else:
        status = 200
        df.annotation = request.form['annotation']
        db.session.add(df)
        db.session.commit()
        content = df.to_json_dict()

    response = jsonify(content)
    response.status_code = status
    return response


#
# Static routes that real directory structure.

@main.route('/dicom/raw/<string:filename>', methods=['GET'])
def get_raw_dicom(filename):
    upload_dir = current_app.config['DICOM_ABS_UPLOAD_DIR']
    return send_from_directory(upload_dir, filename)


@main.route('/dicom/img/<string:filename>', methods=['GET'])
def get_img(filename):
    upload_dir = current_app.config['IMG_ABS_UPLOAD_DIR']
    return send_from_directory(upload_dir, filename)
