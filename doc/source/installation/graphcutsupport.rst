======================================
Installing MedPy with GraphCut support
======================================
The GraphCut functionalities of **MedPy** depend on the `max-flow/min-cut library <http://vision.csd.uwo.ca/code/>`_ by Boykov and Kolmogorov.
During installation, **MedPy** will try to compile it and its python wrappers. If the compilation fails, **MedPy** will be installed without the GraphCut module.
To enable the GraphCut functionality of **MedPy**, the dependencies of the library must be met *before* installing **MedPy** (although it can always be simply re-installed).

Dependencies
------------
* Boost.Python
* g++
* gcc

These dependencies can be found in the repositories of all major distribution. For e.g. Ubuntu, you can simply call:

.. code-block:: bash

	sudo apt-get install libboost-python-dev build-essential

Then install **MedPy** the usual way.
