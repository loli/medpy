# MedPy's CI/CD workflows

## Build & release
Upon creating a release or a pre-release on GitHub, the package is *build* and *published* to [test.pypi.org](https://test.pypi.org).

Install from test PyPi with `python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple medpy==x.y.z.`. This ensures that the dependencies are installed from the proper PyPI.

After making sure that the package published there is installable and passes all tests, the final *publish* to [pypi.org](https://pypi.org) can be triggered manually from the GitHub UI.

Note that publishing only works for releases created directly from the `master` branch. Releasees published from other branches should always be pre-releases and never published to [pypi.org](https://pypi.org), but only [test.pypi.org](https://test.pypi.org).

## pre-commit.yml
Makes sure that all PRs and all releases adhere to the pre-commit rules.

## run-test*.yml
Makes sure that all PRs and all releases pass the tests.
