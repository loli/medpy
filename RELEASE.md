# Steps for a new release

## Preparations
- Create a branch `Release_x.y.z` to work towards the release
- Bump up the library version
    - `setup.py`
    - `medpy/__init__.py`
    - `doc/source/conf.py`
- Run tests and make sure that all work
- Run notebooks and make sure that all work
- Check documentation and make sure that up to date
- Update `CHANGES.txt`, highlighting only major changes
- Test releases by publishing a pre-release, using the workflow detailed under [.github/workflows](.github/workflows)
- Re-create documentation and upload to gihub pages to test, then revert to previous version


## Release
- Open PR to master, review, and merge
- Create a pre-release from master and test
- Create final release from master and test
- Trigger publish to PyPi workflow (see under [.github/workflows](.github/workflows))
- Update conda-force recipe to new version (PR)
- Update DOI

## Further readings
- https://packaging.python.org/
- https://docs.github.com/en/actions
