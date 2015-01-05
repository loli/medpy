==========================================
Installing ITK wrappers for Python (ITKv4)
==========================================
The switch from ITKv3 to ITKv4 includes a large number of changes, also affecting the way the Python wrappers are to be compiled. Here you can find a thorough step-by-step description on how to compile them with ITKv4 (more precisely 4.7) on POSIX/Unix platforms (more precisely Ubuntu14.04).
This is quite some work and absolutely not fail-save. Only try it, if you must (or are bored with too much time at hand).

Getting ITK
***********
Got to http://www.itk.org/ITK/resources/software.html , download the *InsightToolkit-4.7.0.tar.gz* resp. *InsightToolkit-4.7.0.zip* archive and unpack it to a folder called somthing like *IKT4.7.0/src*.

Getting PyBuffer
****************
To be able to convert between ITK images and Numpy arrays, we require PyBuffer. As a novelty compared to ITKv3, this external tool can now be installed as ITK module and the known bug has finally been fixed. Simply run:

.. code-block:: bash

    git clone https://github.com/tobiasmaier/itkPyBuffer.git IKT4.7.0/src/Modules/External/PyBuffer
    
.. note::
    The Insight Software Consortium (ITK developers) just recently forked PyBuffer and started their own development branch under https://github.com/InsightSoftwareConsortium/ITKBridgeNumPy . Best keep an eye on this.

Configuring ITK
***************
Compiling ITK requires *cmake* and, for convenience, **ccmake** which can be found for almost all platforms. Create a new directory *IKT4.7.0/build* and enter it. Then run:

.. code-block:: bash

	ccmake ../src

and subsequently hit the *c* key to configure the build. When finished, hit the *t* key to toggle the advanced mode and activate the following options::

    BUILD_SHARED_LIBS       ON
    ITK_WRAP_PYTHON         ON
    ITK_LEGACY_SILENT       ON

, then *c* configure again. Ignore the warning by pressing *e*. Now set the following options::

    ITK_WRAP_DIMS           2;3;4

    ITK_WRAP_float          ON
    ITK_WRAP_double         ON
    ITK_WRAP_signed_char    ON
    ITK_WRAP_signed_long    ON
    ITK_WRAP_signed_short   ON
    ITK_WRAP_unsigned_char  ON
    ITK_WRAP_unsigned_long  ON
    ITK_WRAP_unsigned_short ON
	WRAP_<data-type>	        Select yourself which more to activate.

, and *c* configure another time. Finally press *g* to generate the make-file.

If *cmake* signals any errors during the configuration process, try to resolve the dependencies from which they originate. Especially PyBuffer sometimes signals `Numpy not found.  Please set PYTHON_NUMARRAY_INCLUDE_DIR`, in which case you will have to set::

    PYTHON_NUMARRAY_INCLUDE_DIR     /usr/include/numpy

Compiling ITK
*************
Now that the configuration is done, we can compile ITK. Run:

.. code-block:: bash

	make -j<number-of-your-porcessors>

and wait. This will take some time, depending on your computer up to 2 days are not unlikely. This is because the Python Wrappers require ITK to instantiate all possible data type combinations for their templates, which increases exponentially which each activated data-type.

If an error occurs, try to understand it and eventually re-run the previous step with some options changed.

Installing ITK
**************
Install ITK and its Python bindings simply by running:

.. code-block:: bash

	make install (as root)

Congratulations, you are done compiling and installing ITK with Python wrappers.

