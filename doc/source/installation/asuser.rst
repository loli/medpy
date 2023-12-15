========================
Installing MedPy as user
========================
.. note::

    All installation instructions are for Debian derivates,
    such as Ubuntu, but they should be simmilar for other distributions.

The local install will place **MedPy** in your user site-packages directory and does not require root privileges. You can find our the location of your personal site-packages directory by calling:

.. code-block:: bash

	python -c 'import site;print site.USER_SITE'

In some cases, the Python configuration does not find packages in the users site-packages directory, in which case you will have to add it to your PYTHONPATH variable.
To make this permanent, add the extension to your `.bashrc`, e.g. using:

.. code-block:: bash

	echo "export PYTHONPATH=${PYTHONPATH}:$( python -c 'import site;print site.USER_SITE' )" >> ~/.bashrc

More importantly, the script shipped with **MedPy** won't be in your PATH and hence can not be used directly. If your user site-packages directory is
e.g. `/home/<user>/.local/lib/python2.7/site-packages/`, the scripts are most likely to be found under `/home/<user>/.local/bin/`. Add this directory to your PATH using:

.. code-block:: bash

	 echo "export PATH=${PATH}:/home/<user>/.local/bin/" >> ~/.bashrc

(Don't forget to replace <user> with your own user name.)

Installing using `PIP <https://pypi.python.org/pypi/pip>`_
----------------------------------------------------------
Requires `PIP <https://pypi.python.org/pypi/pip>`_ to be installed on your machine.

To enable the graph-cut package, we also need the following, which required administrator rights.
If you do not plan on using the graph-cut functionality of **MedPy**, you can skip this step.

.. code-block:: bash

    sudo apt-get install libboost-python-dev build-essential

To install **MedPy** itself, simply call

.. code-block:: bash

    pip install --user medpy


Installing from source
----------------------
No PIP? Download the sources from https://pypi.python.org/pypi/MedPy/, unpack them, enter the directory and run

.. code-block:: bash

    python setup.py install --user
