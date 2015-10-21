/** @jsx React.DOM */
(function() {
    var DicomPage = React.createClass({displayName: "DicomPage",
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
                React.createElement("div", {id: "dicom_page"}, 
                    React.createElement("h1", null, "Dicom File Viewer"), 
                    React.createElement(DicomUploader, {
                        onUpload: this._onUpload}), 
                    React.createElement(DicomTable, {
                        needsUpdate: this.state.tableNeedsUpdate, 
                        onUpdate: this._onUpdate})
                )
            )
        }
    });

    var DicomUploader = React.createClass({displayName: "DicomUploader",
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
                    React.createElement("span", {className: "upload-spinner"}, 
                        React.createElement("img", {src: "/static/img/spinner.gif"})
                    )
                );
            } else {
                spinner = React.createElement("span", null)
            }

            return (
                React.createElement("div", {id: "dicom-uploader-component"}, 
                    React.createElement("div", null, queuedFiles.length, " file(s) ready for upload "), 
                    React.createElement("ul", null, 
                        queuedFiles.map(function(f, k) {
                            return (
                                React.createElement("li", {key: k}, 
                                    f.name, " ", React.createElement("a", {className: "icon delete-icon", href: "#", 
                                        onClick: self._removeFile.bind(this, f.name)})
                                )
                            )
                        })
                    ), 

                    React.createElement("label", {htmlFor: "file-upload", 
                           className: "dicom-upload-btn"}, "Add More"), 
                    React.createElement("input", {type: "file", id: "file-upload", 
                           multiple: "multiple", 
                           onChange: this._addFiles}), 
                    React.createElement("button", {
                        className: "dicom-upload-btn", 
                        onClick: this._uploadQueued, 
                        disabled: this.state.uploading ? "" : ""
                    }, "Upload All"), 
                    spinner, 
                    React.createElement("span", {className: "upload-error"}, this.state.uploadError)
                )
            );
        }
    });

    var DicomTable = React.createClass({displayName: "DicomTable",
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
                    React.createElement("span", {className: "table-spinner"}, 
                        React.createElement("img", {src: "/static/img/spinner.gif"})
                    )
                )
            } else {
                content = (
                    React.createElement("span", null, "No Dicom files are available. Please upload more.")
                );
            }

            return (
                React.createElement("tr", null, 
                    React.createElement("td", {colSpan: "10"}, content)
                )
            )
        },
        render: function() {
            var self = this,
                files = this.state.dicomFiles;
            return (
                React.createElement("div", {id: "dicom-table-component"}, 
                    React.createElement("table", {id: "dicom-table"}, 
                        React.createElement("thead", null, 
                            React.createElement("tr", null, 
                                React.createElement("th", null, "ID"), 
                                React.createElement("th", null, "Filename"), 
                                React.createElement("th", null, "Study Date"), 
                                React.createElement("th", null, "Patient Name"), 
                                React.createElement("th", null, "Patient Sex"), 
                                React.createElement("th", null, "Patient Age"), 
                                React.createElement("th", null, "Image"), 
                                React.createElement("th", null, "Annotation"), 
                                React.createElement("th", null, "-")
                            )
                        ), 
                        React.createElement("tbody", null, 
                            files.map(function(df) {
                                return (
                                    React.createElement("tr", {key: df.id}, 
                                        React.createElement("td", null, df.id), 
                                        React.createElement("td", null, React.createElement("a", {href: df.raw_url}, df.filename)), 
                                        React.createElement("td", null, df.study_date), 
                                        React.createElement("td", null, df.patient.name), 
                                        React.createElement("td", null, df.patient.sex), 
                                        React.createElement("td", null, df.patient.age), 
                                        React.createElement("td", null, 
                                            React.createElement("a", {href: df.img_url}, 
                                                React.createElement("img", {src: df.thumb_url})
                                            )
                                        ), 
                                        React.createElement("td", {className: "annotation-row"}, 
                                            React.createElement(AnnotationRow, {
                                                df: df, 
                                                updateAnnotation: function(a) {
                                                    df.annotation = a;
                                                }})
                                        ), 
                                        React.createElement("td", null, React.createElement("a", {href: "#", 
                                               className: "icon delete-icon", 
                                               onClick: self._removeFile.bind(self, df.id)}
                                            )
                                        )
                                    )
                                );
                            }), 
                            this._renderEmptyPlaceholder(files.length === 0)
                        )
                    )
                )
            );
        }
    });

    var AnnotationRow = React.createClass({displayName: "AnnotationRow",
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
                React.createElement("span", null, 
                    React.createElement("input", {type: "text", 
                           defaultValue: this.props.df.annotation, 
                           onKeyDown: this._handleKeyDown})
                )
            );
        },
        _renderView: function() {
            var self = this;
            return (
                React.createElement("span", null, 
                    React.createElement("a", {href: "#", className: "icon edit-icon", 
                        onClick: function() {
                            self.setState({editing: true})
                        }
                    }), 
                    this.props.df.annotation || '(None)'
                )
            );
        },
        render: function() {
            return (
                React.createElement("span", null, 
                    this.state.editing ? this._renderEditing() :
                                          this._renderView()
                )
            )
        }
    })

    window.exports = window.exports || {};
    window.exports.DicomPage = DicomPage;
}());
