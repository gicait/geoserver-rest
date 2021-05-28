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

In windows, the ``gdal`` dependency can be install using ``pipwin``,

.. code-block:: shell

    pip install pipwin
    pipwin refresh
    pipwin install gdal

Now you can install the library using pip install command,

.. code-block:: shell

    pip install geoserver-rest


Linux installation
------------------

In Debian/Ubuntu, ``gdal`` can be installed using following method:

.. code-block:: shell

    sudo add-apt-repository ppa:ubuntugis/ppa
    sudo apt update -y; sudo apt upgrade -y;
    sudo apt install gdal-bin libgdal-dev
    pip3 install pygdal=="`gdal-config --version`.*"

Now the geoserver-rest library can be installed using pip install command:

.. code-block:: shell

    pip install geoserver-rest
