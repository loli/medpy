=======================
MedPy docker containers
=======================

*Warning:* The docker containers are no longer maintained.

What is docker?
---------------
Docker (https://www.docker.com/) is a new and convenient way to collect all of an applications requirements in one container and then run it on any system independently of the host system. A layer-based approach allows the re-use of already existing containers and support a hierarchical structure.

Why using MedPy in a docker container?
--------------------------------------
Since the docker container already contains all dependencies and since all required libraries are already compiled, it becomes possible to use and try-out MedPy right out of the box.

MedPy as docker container
-------------------------
MedPy is available as docker containers with a number of configurations::

    * Ubuntu:14.04
        * loli/medpy:dependencies
            * loli/medpy:release
            * loli/medpy:development
            * loli/medpy:itk
                * loli/medpy:release-itk
                * loli/medpy:development-itk
                
Where to find it?
-----------------
Stable versions: https://registry.hub.docker.com/u/loli/medpy/
Autobuilds of the current repository snapshots: https://registry.hub.docker.com/u/loli/medpy-autobuilds/
