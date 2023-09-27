Installation
=============

Conda installation
^^^^^^^^^^^^^^^^^^

The ``geoserver-rest`` can be installed from either ``conda-forge`` channel or ``iamtekson`` channel as below:

.. code-block:: shell

    conda install -c conda-forge geoserver-rest
    conda install -c iamtekson geoserver-rest

Pip installation
^^^^^^^^^^^^^^^^

For installation of this package, following packages should be installed first:

* `GDAL <https://gdal.org/>`_

Windows installation
--------------------

.. warning::
    As of March 2022, ``pipwin`` has been deprecated and is no longer maintained. Do not use this method.

For Windows, the ``gdal`` dependency can be complex to install. There are a handful of ways to install ``gdal`` in Windows.

One way is install the wheel directly from the `Geospatial library wheels for Python Windows <https://github.com/cgohlke/geospatial-wheels>`_ releases page. Be sure to select the wheel for your system from the latest release and install it using pip install command:

.. code-block:: shell

    # For Python3.10 on Windows 64-bit systems
    $ pip install https://github.com/cgohlke/geospatial-wheels/releases/download/<release_version>/GDAL-3.7.1-cp310-cp310-win_amd64.whl

Another way is to use the OSGeo4W network installer binary package available at: https://trac.osgeo.org/osgeo4w/.

Now you can then install the library using pip install command:

.. code-block:: shell

    $ pip install geoserver-rest

macOS installation
------------------

For macOS, we suggest using the `homebrew` package manager to install ``gdal``. Once ``homebrew`` is installed, ``gdal`` can be installed using following method:

.. code-block:: shell

    brew update
    brew install gdal
    pip3 install pygdal=="$(gdalinfo --version | awk '{print $2}' | sed s'/.$//')"

Linux installation
------------------

For Ubuntu specifically, we suggest installing ``gdal`` from the ``ubuntugis`` PPA:

.. code-block:: shell

    $ sudo add-apt-repository ppa:ubuntugis/ppa
    $ sudo apt update -y
    $ sudo apt upgrade -y
    $ sudo apt install gdal-bin libgdal-dev

For other versions of linux, simply use your package manager to install ``gdal``.

.. code-block:: shell

    # Debian, Mint, etc.
    $ sudo apt install gdal-bin libgdal-dev
    # Fedora, RHEL, etc.
    $ sudo yum install gdal gdal-devel
    # Arch, Manjaro, etc.
    $ sudo pacman -S gdal
    # Void
    $ sudo xbps-install -S libgdal libgdal-dev

Now the ``pygdal`` and ``geoserver-rest`` library can be installed using pip install command:

.. code-block:: shell

    $ pip install pygdal=="`gdal-config --version`.*"
    $ pip install geoserver-rest
