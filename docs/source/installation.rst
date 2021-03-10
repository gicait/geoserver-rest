Installation
=============

Conda installation
^^^^^^^^^^^^^^^^^^^

The ``geoserver-rest`` can be installed from either ``conda-forge`` channel or ``iamtekson`` channel as below,

.. code-block:: shell

    conda install -c conda-forge geoserver-rest
    conda install -c iamtekson geoserver-rest

Pip installation
^^^^^^^^^^^^^^^^^

For installation of this package, following packages should be installed first:

* `GDAL <https://gdal.org/>`_
* `Pycurl <http://pycurl.io/>`_ (This dependency will be replaced by python request in v2.0.0)


Windows installation
----------------------

In windows, the ``gdal`` and ``pycurl`` dependencies can be install using ``pipwin``,

.. code-block:: shell

    pip install pipwin
    pipwin refresh
    pipwin install gdal
    pipwin install pycurl
    
Now you can install the library using pip install command,

.. code-block:: shell

    pip install geoserver-rest


Ubuntu installation
---------------------

In ubuntu, The ``gdal`` and ``pycurl`` dependencies can be install using following method,

.. code-block:: shell

    sudo add-apt-repository ppa:ubuntugis/ppa
    sudo apt update -y; sudo apt upgrade -y;
    sudo apt install gdal-bin libgdal-dev python3-pycurl
    pip3 install pygdal=="`gdal-config --version`.*"


Now the geoserver-rest library can be installed using pip install command,

.. code-block:: shell

    pip install geoserver-rest

    


  
