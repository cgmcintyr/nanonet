.PHONY: install develop deb clean venv_osx osx_develop osx_nanonetcall osx_zmqcall osx_api

install:
	python setup.py install

develop: clean
	python setup.py develop --user

deb: clean
	touch tmp
	rm -rf tmp *.deb
	python setup.py --command-packages=stdeb.command bdist_deb

clean:
	python setup.py clean
	rm -rf build/ dist/ deb_dist/ *.egg-info/
	find . -name '*.pyc' -delete
	find . -name '*.so' -delete




venv_osx: venv_osx/bin/activate

venv_osx/bin/activate:
	test -d venv || virtualenv venv_osx --python=python3
	. ./venv_osx/bin/activate && pip install numpy
	touch venv_osx/bin/activate

osx_develop: venv_osx
	. ./venv_osx/bin/activate && python setup.py develop
	cp nanonetdecode.cpython-36m-darwin.so nanonetdecode.so
	cp nanonetfilters.cpython-36m-darwin.so nanonetfilters.so

venv_osx/bin/pyinstaller: venv_osx
	. ./venv_osx/bin/activate && pip install git+git://github.com/pyinstaller/pyinstaller.git@a98be396ed9a14799bdea8aaae68d2f6ae43bd03

osx_nanonetcall: osx_develop venv_osx/bin/pyinstaller
	. ./venv_osx/bin/activate && venv_osx/bin/pyinstaller nanonetcall.spec nanonetcall.spec

osx_zmqcall: osx_develop venv_osx/bin/pyinstaller
	. ./venv_osx/bin/activate && pip install pyzmq zmq aiozmq msgpack-python
	. ./venv_osx/bin/activate && venv_osx/bin/pyinstaller zmqcall.spec

