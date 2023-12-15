========================
Installing MedPy as root
========================
.. note::

    All installation instructions are for Debian derivates,
    such as Ubuntu, but they should be simmilar for other distributions.

When installed with root privileges, **MedPy** will be available for all uses of your machine.

To install Python packages from `PyPi <https://pypi.python.org>`_, we recommend `PIP <https://pypi.python.org/pypi/pip>`_.
To enable the graph-cut package, we need the following

.. code-block:: bash

    sudo apt-get install libboost-python-dev build-essential

Now we can install **MedPy**

.. code-block:: bash

    sudo pip install medpy
