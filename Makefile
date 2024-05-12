test:
	tox

publish: clean
	python setup.py sdist bdist_wheel
	twine upload -s dist/*

clean:
	rm -rf *.egg-info *.egg dist build .pytest_cache
	rm -rf .tox/py* .tox/dist/*

.PHONY: test publish clean
