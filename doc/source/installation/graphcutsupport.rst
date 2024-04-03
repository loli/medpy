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

Troubleshooting
---------------

If you experience an error like `ModuleNotFoundError: No module named 'medpy.graphcut.maxflow'`, this usually means
that the `graphcut` module has not been compiled successfully. To check the error log, try re-installing **MedPy** with:

.. code-block:: bash

	pip install medpy --no-cache-dir --force-reinstall -v

In the logs, you might see the following warning:

::

	2021-06-30T11:07:32,684   ***************************************************************************
	2021-06-30T11:07:32,685   WARNING: The medpy.graphcut.maxflow external C++ package could not be compiled, all graphcut functionality will be disabled. You might be missing Boost.Python or some build essentials like g++.
	2021-06-30T11:07:32,685   Failure information, if any, is above.
	2021-06-30T11:07:32,685   I'm retrying the build without the graphcut C++ module now.
	2021-06-30T11:07:32,685   ***************************************************************************

The error should be detailed in the lines just above.

Usually, it is a problem with the linking of the `(lib)boost_python3` lib.
There are some inconsistent naming conventions around, rendering the file undiscoverable to **MedPy**.

On Ubuntu, you should be able to locate your *libboost_python3x.so* under `/usr/lib/x86_64-linux-gnu/`.
If your shared library file is named differently than **MedPy** expects, you might have to create a softlink like, e.g.:

.. code-block:: bash

	sudo ln -s libboost_python38.so libboost_python3.so
