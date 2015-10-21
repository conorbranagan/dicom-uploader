/** @jsx React.DOM */
(function() {
    var DicomPage = React.createClass({
        _onUpload: function() {
            this.setState({tableNeedsUpdate: true});
        },
        _onUpdate: function() {
            this.setState({tableNeedsUpdate: false})
        },
        getInitialState: function() {
            return {
                tableNeedsUpdate: false
            };
        },
        render: function() {
            return (
                <div id="dicom_page">
                    <h1>Dicom File Viewer</h1>
                    <DicomUploader
                        onUpload={this._onUpload} />
                    <DicomTable
                        needsUpdate={this.state.tableNeedsUpdate}
                        onUpdate={this._onUpdate} />
                </div>
            )
        }
    });

    var DicomUploader = React.createClass({
        /*
         * props:
         *    - onUpload: Callback for a succesful upload.
         */
        _addFiles: function(e) {
            e.preventDefault();

            // Queue the files to our list.
            var queuedFiles = this.state.queuedFiles,
                inputFiles = e.target.files;
            for (var i = 0; i < inputFiles.length; i++) {
                queuedFiles.push(inputFiles[i]);
            }
            this.setState({
                queuedFiles: queuedFiles
            });

            // Reset the input.
            e.target.value = '';
        },
        _removeFile: function(name, e) {
            e.preventDefault();
            var queuedFiles = this.state.queuedFiles.filter(function(v) {
                return v.name !== name;
            });
            this.setState({
                queuedFiles: queuedFiles,
                uploadError: ''
            });
        },
        _uploadQueued: function(e) {
            var self = this;
            if (this.state.queuedFiles.length === 0) {
                // Ignore upload button if nothing is queued.
                return;
            }

            var formData = new FormData();
            this.state.queuedFiles.forEach(function(f, k) {
                formData.append(k, f);
            });

            this.setState({uploading: true});

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/dicom', true);
            xhr.onload = function(e) {
                if (this.status === 200) {
                    self.setState({
                        queuedFiles: [],
                        uploading: false,
                        uploadError: ''
                    });
                    self.props.onUpload();
                } else {
                    var response = JSON.parse(this.response);
                    self.setState({
                        uploading: false,
                        uploadError: 'Error: ' + response.error
                    });
                }
            }
            xhr.send(formData);
        },

        getInitialState: function() {
            return {
                uploading: false,
                uploadError: '',
                queuedFiles: []
            };
        },
        render: function() {
            var queuedFiles = this.state.queuedFiles;
            var self = this;
            if (this.state.uploading) {
                spinner = (
                    <span className="upload-spinner">
                        <img src="/static/img/spinner.gif" />
                    </span>
                );
            } else {
                spinner = <span></span>
            }

            return (
                <div id="dicom-uploader-component">
                    <div>{queuedFiles.length} file(s) ready for upload </div>
                    <ul>
                        {queuedFiles.map(function(f, k) {
                            return (
                                <li key={k}>
                                    {f.name} <a className="icon delete-icon" href="#"
                                        onClick={self._removeFile.bind(this, f.name)}></a>
                                </li>
                            )
                        })}
                    </ul>

                    <label htmlFor="file-upload"
                           className="dicom-upload-btn">Add More</label>
                    <input type="file" id="file-upload"
                           multiple="multiple"
                           onChange={this._addFiles} />
                    <button
                        className="dicom-upload-btn"
                        onClick={this._uploadQueued}
                        disabled={this.state.uploading ? "" : ""}
                    >Upload All</button>
                    {spinner}
                    <span className="upload-error">{this.state.uploadError}</span>
                </div>
            );
        }
    });

    var DicomTable = React.createClass({
        /*
         * props:
         *    - onUpdate: Callback for a succesful table update.
         *    - needsUpdate: Indicates if the table should update.
         */

        _loadFiles: function() {
            // Load dicom files from the backend API.
            var self = this,
                xhr = new XMLHttpRequest();

            xhr.open('GET', '/dicom', true);
            xhr.onload = function(e) {
                if (this.status === 200) {
                    var response = JSON.parse(this.response);
                    self.setState({
                        loading: false,
                        dicomFiles: response.dicom_files
                    });
                    self.props.onUpdate();
                }
            }
            xhr.send();
        },
        _removeFile: function(fileID) {
            var xhr = new XMLHttpRequest();
            xhr.open('DELETE', '/dicom/' + fileID, true);
            xhr.send();

            this.setState({
                dicomFiles: this.state.dicomFiles.filter(function(df) {
                    return df.id !== fileID
                })
            });
        },

        getInitialState: function() {
            return {
                loading: true,
                dicomFiles: []
            };
        },
        componentDidMount: function() {
            this._loadFiles();
        },
        componentWillReceiveProps: function(nextProps) {
            if (nextProps.needsUpdate) {
                this._loadFiles();
            }
        },
        _renderEmptyPlaceholder: function(isEmpty) {
            if (!isEmpty) return;
            var content;
            if (this.state.loading) {
                content = (
                    <span className="table-spinner">
                        <img src="/static/img/spinner.gif" />
                    </span>
                )
            } else {
                content = (
                    <span>No Dicom files are available. Please upload more.</span>
                );
            }

            return (
                <tr>
                    <td colSpan="10">{content}</td>
                </tr>
            )
        },
        render: function() {
            var self = this,
                files = this.state.dicomFiles;
            return (
                <div id="dicom-table-component">
                    <table id="dicom-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Filename</th>
                                <th>Study Date</th>
                                <th>Patient Name</th>
                                <th>Patient Sex</th>
                                <th>Patient Age</th>
                                <th>Image</th>
                                <th>Annotation</th>
                                <th>-</th>
                            </tr>
                        </thead>
                        <tbody>
                            {files.map(function(df) {
                                return (
                                    <tr key={df.id}>
                                        <td>{df.id}</td>
                                        <td><a href={df.raw_url}>{df.filename}</a></td>
                                        <td>{df.study_date}</td>
                                        <td>{df.patient.name}</td>
                                        <td>{df.patient.sex}</td>
                                        <td>{df.patient.age}</td>
                                        <td>
                                            <a href={df.img_url}>
                                                <img src={df.thumb_url} />
                                            </a>
                                        </td>
                                        <td className="annotation-row">
                                            <AnnotationRow
                                                df={df}
                                                updateAnnotation={function(a) {
                                                    df.annotation = a;
                                                }} />
                                        </td>
                                        <td><a href="#"
                                               className="icon delete-icon"
                                               onClick={self._removeFile.bind(self, df.id)}>
                                            </a>
                                        </td>
                                    </tr>
                                );
                            })}
                            {this._renderEmptyPlaceholder(files.length === 0)}
                        </tbody>
                    </table>
                </div>
            );
        }
    });

    var AnnotationRow = React.createClass({
        /**
         * props:
         *    - df: Dicom file object.
         *    - updateAnnotation: Callback to update the annotation.
         */
        getInitialState: function() {
            return {
                editing: false
            };
        },

        _handleKeyDown: function(e) {
            var self = this;
            if (e.key === 'Enter') {

                // Send annotation to the backend and go back to view.
                e.target.disabled = 'disabled';

                var xhr = new XMLHttpRequest(),
                    formData = new FormData(),
                    newVal = e.target.value;
                formData.append('annotation', e.target.value);

                xhr.open('POST', '/dicom/annotate/' + self.props.df.id, true);
                xhr.onload = function(e) {
                    self.props.updateAnnotation(newVal);
                    e.target.disabled = '';
                    self.setState({
                        editing: false
                    });
                }
                xhr.send(formData);
            }
        },
        _renderEditing: function() {
            return (
                <span>
                    <input type="text"
                           defaultValue={this.props.df.annotation}
                           onKeyDown={this._handleKeyDown} />
                </span>
            );
        },
        _renderView: function() {
            var self = this;
            return (
                <span>
                    <a href="#" className="icon edit-icon"
                        onClick={function() {
                            self.setState({editing: true})
                        }}
                    ></a>
                    {this.props.df.annotation || '(None)'}
                </span>
            );
        },
        render: function() {
            return (
                <span>
                    {this.state.editing ? this._renderEditing() :
                                          this._renderView()}
                </span>
            )
        }
    })

    window.exports = window.exports || {};
    window.exports.DicomPage = DicomPage;
}());
