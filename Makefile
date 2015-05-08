publish: clean
	python setup.py sdist bdist_wheel
	twine upload dist/*

clean:
	rm -rf *.egg-info *.egg dist build

.PHONY: publish clean
