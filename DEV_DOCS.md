# Documentation

### Publishing the python package

For publishing the python package, follow following steps,

1. Install twine `pip install twine`
2. Generate packages and create dist folder by running setup.py file `python setup.py bdist_wheel sdist`
3. Push to PyPI `twine upload dist/*`

### Pre-commit Reference

To install the additional libraries for dev (testing, formatting, etc.) run `pip install --editable .[dev]`

[`pre-commit`](https://pre-commit.com/) is a pretty standard tooling-helper for automating the formatting of code (`isort`, `black`, `end-of-file-fixer`, `trailing-space-fixer`, etc.) and evaluating any potential issues (`flake8`). This essentially makes all code contributions look the same no matter what in order to favour readability/maintainability.

Installing and running `pre-commit` is fairly automatic. After installing the requirements-dev.txt, run:

```bash
pre-commit install
```

and the environments will be managed automatically. Any calls to git commit will run the checks. If something changes, you need to simply run git commit a second time and it should be good.

Some checks will require changes (e.g. imports of `pdb` are a violation, unused imports, unused initialized objects, etc.). If these are needed by design you can do either of the following:

To commit the files and ignore the checks (not great as checks will fail for future commits and for others):

```bash
git commit --no-verify -m "my message"
```

If you want the violation to be ignored, place a \_\_# noqa (precisely: two empty spaces, #, one empty space, noqa) next to the affected line.
