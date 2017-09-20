==========================================
Installing ITK wrappers for Python (ITKv3)
==========================================
This is quite some work and absolutely not fail-save. Only try it, if you must (or are bored with too much time at hand).

1. Installing ITK with Python binding on Ubuntu (>= 10.04)
----------------------------------------------------------
The Ubuntu repositories provide a package which can simply be installed using:

.. code-block:: bash
	
	sudo apt-get install python-insighttoolkit3

But this package wraps only a subset of ITKs functionality and therefore does not unleash **MedPy** s complete power. The recommendation is to follow the second or third approach.

2. Installing ITK with Python binding on Ubuntu (= 12.04)
---------------------------------------------------------
If you are running Ubuntu 12.04, you can simply contact the author who will provide you with a pre-compiled Ubuntu package.

3. Compiling ITK with Python bindings on POSIX/Unix platforms
-------------------------------------------------------------
All descriptions are for ITK 3.20 but might also be valid for newer versions.

Getting ITK
***********
Got to http://www.itk.org/ITK/resources/software.html , download the *InsightToolkit-3.20.1.tar.gz* resp. *InsightToolkit-3.20.1.zip* archive and unpack it to a folder called somthing like *IKT3.20.1/src*.

Configuring ITK
***************
Compiling ITK requires *cmake* which can be found for almost all platforms. Create a new directory *IKT3.20.1/build* and enter it. Then run:

.. code-block:: bash

	ccmake ../src

and subsequently hit the *c* key to configure the build. When finished, hit the *t* key to toggle the advanced mode and activate the following options::

	BUILD_SHARED_LIBS ON
	ITK_USE_REVIEW	  ON
	USE_WRAP_ITK	  ON

, then *c* onfigure again. Ignore the warning by pressing *e*. Now set the following options::

	WRAP_FFT	    OFF
	WRAP_ITK_DIMS	    2;3;4 (or more, if you require)
	WRAP_ITK_JAVA	    OFF
	WRAP_ITK_PYTHON	    ON
	WRAP_ITK_TCL	    OFF

	WRAP_double         ON
	WRAP_float          ON
	WRAP_signed_char    ON
	WRAP_signed_long    ON
	WRAP_signed_short   ON
	WRAP_unsigned_char  ON
	WRAP_unsigned_long  ON
	WRAP_unsigned_short ON
	WRAP_<datatype>	  Select yourself which more to activate.

, and *c* onfigure another time. Finally press *g* to generate the make-file.

If *cmake* signals any errors during the configuration process, try to resolve the dependencies from which they originate.

Compiling ITK
*************
Now that the configuration is done, we can compile ITK. Run:

.. code-block:: bash

	make -j<number-of-your-porcessors>

and wait. This will take some time, depending on your computer up to 2 days are not unlikely.


If an error occurs, try to understand it and eventually re-run the previpous step with some options changed.

Installing ITK
**************
Install ITK and its Python bindings simply by running:

.. code-block:: bash

	make install (as root)

Addditional step
****************
The ITK Python bindings require a third-party module called PyBuffer which is shipped with ITK but not automatically compiled. Furthermore it holds a small bug. After finishing the previous steps, create a folder called *PyBuffer/src* somewhere and copy all files and folders from *ITK/src/Wrapping/WrapITK/ExternalProjects/PyBuffer/* into it. Now open *itkPyBuffer.txx* with an text editor and change the line:
	
.. code-block:: cpp

	int dimensions[ ImageDimension ];

to:

.. code-block:: cpp

	npy_intp dimensions[ ImageDimension ];

(see http://code.google.com/p/wrapitk/issues/detail?id=39 for patch details). Then create a folder *PyBuffer/build*, enter it and run:

.. code-block:: bash

	ccmake ../src

After *c* onfiguring you will see some warnings. Set::

	WrapITK_DIR	ITK/bin/Wrapping/WrapITK/

In some cases you will also have to set::

	PYTHON_NUMARRAY_INCLUDE_DIR	/usr/include/numpy

Now *c* onfigure again and *g* enerate. To finalize run::

.. code-block:: bash

	make
	make install (as root)

Congratulations, you are done compiling and installing ITK with Python wrappers.

