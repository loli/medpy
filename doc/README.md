# Building the HTML documentation

Install MedPy with the `[doc]` extras

    pip3 install medpy[doc]

Then run in `docs/`

    sphinx-build -aE -b html source/ build/

You can now find the HTML files in the `build/` folder.
