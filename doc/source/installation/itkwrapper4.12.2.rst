===============================================
Installing ITK wrappers for Python (ITKv4.12.2)
===============================================
The ITK consortium does not cease to change its python bindings at every turn. Starting from 4.12, the `PyBuffer module <https://github.com/InsightSoftwareConsortium/ITKBridgeNumPy>`_ is (again) included in the library. Here you can find a thorough step-by-step description on how to compile them with ITKv4 (more precisely 4.12.2) on POSIX/Unix platforms (more precisely Ubuntu16.04).
This is quite some work and absolutely not fail-save. Only try it, if you must (or are bored with too much time at hand).

Getting ITK
***********
Got to http://www.itk.org/ITK/resources/software.html , download the *InsightToolkit-4.12.2.tar.gz* resp. *InsightToolkit-4.12.2.zip* archive and unpack it to a folder called somthing like *IKT4.12.2/src*.

Configuring ITK
***************
Compiling ITK requires *cmake* and, for convenience, **ccmake** which can be found for almost all platforms. Create a new directory *IKT4.12.2/build* and enter it. Then run:

.. code-block:: bash

	ccmake ../src

and subsequently hit the *c* key to configure the build. When finished, hit the *t* key to toggle the advanced mode and activate the following options::

    ITK_WRAP_PYTHON             ON
    ITK_LEGACY_SILENT           ON
    Module_BridgeNumPy          ON    

, then *c* configure again. Ignore any warning for now by pressing *e*. Now set the following options::

    ITK_WRAP_DIMS               2;3;4
    ITK_WRAP_VECTOR_COMPONENTS  2;3;4

    ITK_WRAP_float              ON
    ITK_WRAP_double             ON
    ITK_WRAP_signed_char        ON
    ITK_WRAP_signed_long        ON
    ITK_WRAP_signed_short       ON
    ITK_WRAP_unsigned_char      ON
    ITK_WRAP_unsigned_long      ON
    ITK_WRAP_unsigned_short     ON
    ITK_WRAP_vector_float       ON
	  WRAP_<data-type>	          Select yourself which more to activate.

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

Can I use them appart from MedPy?
*********************************
Naturally. Check https://github.com/InsightSoftwareConsortium/ITKBridgeNumPy for an introduction.

