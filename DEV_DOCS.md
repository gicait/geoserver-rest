# Documentation

For publishing the python package, follow following steps,
1. install twine `pip install twine`
2. create dist folder by running setup.py file `python setup.py bdist_wheel sdist`
3. Push to PyPI `twine upload dist/*`