PATH := node_modules/.bin:$(PATH)

.PHONY: docs test

help:
	@echo "  env         create a development environment using virtualenv"
	@echo "  run         run the web app server"
	@echo "  clean       remove unwanted files like .pyc's"
	@echo "  clean_all   reset the workspace completely"
	@echo "  lint        check style with flake8"
	@echo "  test        run all your tests using py.test"
	@echo "  static      compile static files for use with the app"

run:
	. py3/bin/activate && python manage.py server

clean:
	. py3/bin/activate && python manage.py clean
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

clean_all:
	make clean
	rm -rf node_modules
	rm -rf py3
	rm -rf dicom_upload/static/js/build/.module-cache/*

lint:
	. py3/bin/activate && flake8 --exclude=py3 .

test:
	. py3/bin/activate && py.test tests

static:
	jsx --extension jsx dicom_upload/static/js/src/ dicom_upload/static/js/build/