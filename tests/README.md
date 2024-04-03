# MedPy unittests

Part of the MedPy functionality is covered by unittests in various states
of development which can be found in this folder. See instructions below
for instructions.

## Run for sub-module
```
pytest tests/<submodule>_/*
```

Note: `metric_/` sub-module requires hypothesis package

## Check support for image formats
```
pytest -s tests/io_/loadsave.py > myformats.log
pytest -s io_/metadata.py > mymetacompatibility.log

more myformats.log
more mymetacompatibility.log
```

Note that this will take some time and producte a number of warnings that can be savely ignored.
