========================
Installing MedPy as user
========================
.. note::

    All installation instructions are for Ubuntu, but they will work similar for other distributions.

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

First install the Python requirements locally

.. code-block:: bash

    pip install --user numpy scipy nibabel pydicom
    
and then **MedPy**

.. code-block:: bash

    pip install --user medpy


Installing using `easy_install <https://pypi.python.org/pypi/setuptools>`_
--------------------------------------------------------------------------
Requires `easy_install <https://pypi.python.org/pypi/setuptools>`_ to be installed on your machine.

First install the Python requirements locally

.. code-block:: bash

    easy_install --user numpy scipy nibabel pydicom
    
and then **MedPy**

.. code-block:: bash

    easy_install --user medpy

Installing from source
----------------------
No PIP, easy_install or a friendly administrator? There is one last option.
First, install `numpy <http://www.numpy.org/>`_, `scipy <http://www.scipy.org/>`_, 
`nibabel <http://nipy.org/nibabel/>`_ and `pydicom <https://code.google.com/p/pydicom/>`_
from source (see there respective webpages for details) as user.

The download the sources from https://pypi.python.org/pypi/MedPy/, unpack them, enter the directory and run::

.. code-block:: bash

    python setup.py install --user

How do I enable the graph-cut packages
--------------------------------------
The graph-cut package shipped with **MedPy** requires Boost.Python and some standard C++ building tools.
If these are not available during the installation, the package will not be compiled.
You will have to ask your administrator to install the requirements for you (before installing **MedPy**):

.. code-block:: bash
    
    sudo apt-get install libboost-python-dev build-essential


