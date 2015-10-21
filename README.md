# Dicom Uploader

A simple web application for uploading and viewing Dicom files.

The Python code is written against and only tested with Python 3.4. It may work with other Python 3.x versions but it will likely _not_ work with 2.x as it's uses some APIs that changed in the upgrade.

On the frontend side we're using React.js + vanilla JS for everything else. jQuery could have been used for XHR but since we weren't taking advantage of jQuery's main use-case of DOM manipulation I figured I'd save the extra library overhead.

## Setup

Before running any of the Makefile jobs, you'll want to get your environment set up. This should be as simple as running the following command:

```
./bootstrap
```

## Running the server

Run the following:

```
make run
```

Then navigate your browser to `http://localhost:5000/`

## Testing and linting

```
make tests # Run the test suite
make lint  # Run flake8 to lint the code
```

## Notes

Dicom files were tested from a number of places, but the bulk came from the following sites:

- https://mri.radiology.uiowa.edu/visible_human_datasets.html (test data sets are from this)
- http://www.osirix-viewer.com/datasets/

I noticed that there were definitely some differences in the file format. I tried to handle different cases and unhandled files but there may be some cases that are not covered.
