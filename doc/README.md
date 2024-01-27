# Building the HTML documentation

Install sphinx first in your environment. Make sure to have the right version.

    pip3 install sphinx==1.6.7

and test if the right binary is called. Higher versions break with the used numpydoc version.

Then run

    sphinx-build -aE -b html source/ build/

, then edit .rst files belong to Python classes

source/generated/medpy.graphcut.graph.Graph.rst
source/generated/medpy.graphcut.graph.GCGraph.rst
source/generated/medpy.filter.IntensityRangeStandardization.IntensityRangeStandardization.rst
source/generated/medpy.core.logger.Logger.rst
source/generated/medpy.header.Header.rst
source/generated/medpy.iterators.*

by removing the line

    .. automethod:: __init__

and adding the line

    :toctree: generated/

beneath each ".. autosummary::" command.

Finally rerun the build

    sphinx-build -aE -b html source/ build/


## Enabling the search box

Remove

    scipy-sphinx-theme/_theme/scipy/searchbox.html

from the scipy template, as it somehow overrides the search box with a custom link to edit the .rst files in-place online.


## Generate the API documentation files

Run

    sphinx-apidoc -efF -H MedPy -A "Oskar Maier" -V 0.2 -R 1 -o generated/ ../../medpy/medpy/
