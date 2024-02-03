# Steps to do a new release

## Preparations
- Create a branch `Release_x.y.z` to work towards the release
- Bump up the library version
    - `setup.py`
    - `medpy/__init__.py`
    - `doc/source/conf.py`
- Run tests and make sure that all work
- Run notebooks and make sure that all work
- Check documentation and make sure that up to date
- Re-create documentation and upload to gihub pages
- Update `CHANGES.txt`, highlighting only major changes

## Release
- Build package (e.g. with `python -m build`)
- Upload to PyPI
- Update conda-force recipe to new version (PR)
- Update DOI

## Further readings
- https://packaging.python.org/
- https://docs.github.com/en/actions
