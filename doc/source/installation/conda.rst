===========================
Installing MedPy with Conda
===========================

**MedPy** does not come with an official conda package.
But you can nevertheless install it into a conda environement using *pip* after resolving the dependencies.

.. code-block:: bash

	conda install -c simpleitk simpleitk
	pip3 install medpy

Note that the graph-cut package won't compile in the conda environement due to unmet dependencies.

For conda-purists: The friendly folks from `bioconda <https://bioconda.github.io/>`_ wrapped the previous (0.3.0) version of **MedPy**
into their distribution system (see https://anaconda.org/bioconda/medpy).
