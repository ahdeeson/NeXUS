.PHONY: all version wheel doc upload clean

all: wheel doc

version:
	bash change_version.sh

wheel:
	./setup.py sdist bdist_wheel

doc:
	cd doc && $(MAKE) html

upload: clean doc wheel
	twine upload dist/*

clean:
	- cd doc && $(MAKE) clean
	- rm thorlabs_elliptec.egg-info -r
	- rm build -r
	- rm dist -r
	- find . -type d -name __pycache__ -exec rm {} -r \;