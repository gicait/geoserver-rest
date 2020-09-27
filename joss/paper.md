---
title: "Geoserver-rest: A python package for geospatial data management in geoserver"
tags:
  - python
  - geoserver
  - geoserver-rest
  - geospatia data
  - API
authors:
  - name: Tek B. Kshetri
    orcid: 0000-0001-9275-5619
    affiliation: 1
affiliations:
  - name: Research associate, GeoInformatics Center, Asian Institute of Technology
    index: 1
date: 20 September 2020
bibliography: paper.bib
---

# Introduction

The geoserver is the open-source server written in java that allows the user to share, process and edit geospatial data [@Stefano:2017]. Some of the key terms related to geoserver are below.

- **Workspace**: Workspace is the top-level folder of geospatial data storage. It could be useful for categorizing and storing similar kind of datasets. Layers, stores and styles are the subcategories of it [@Colin:2014].

- **Store**: Store is the data source of raster/vector data. It is the connection parameter for the layers. It can be file for the raster data type, can be the file, database or server for the vector data type.

- **Layer**: Layer is the actual dataset that represents the collection of geographic features [@geoserver].

- **Style**: Style is the appearance of layers symbology. It may be different for a different kind of dataset like point, line, polygon, raster. The Style Layer Descriptor (SDS) [@OGC:2007] is the commonly used Symbology Encoding (SE) language [@OGC:2006] proposed by Open Geospatial Consortium [@Bogdanović:2010].

# Summary

The geoserver-rest package is useful for the management for geospatial data in geoserver. It has a comprehensive scope for the web application, mobile application, cloud-based applications development. The geoserver-rest makes it possible to share and manipulate the data between any client-server pair. The geoserver-rest is applicable for creating, updating and deleting geoserver workspaces, stores, layers, and style files.

By default, the geoserver have grey color style. The layer needs to visualize appropriately so that more people can read it easily. it will be more readable if it has proper styling file. The style file can be generated manually from writing the script or with the help of Quantum GIS (QGIS). Generated SLD file needed to be manually uploaded to the geoserver and link it to the layer [@Stefano:2017]. Here comes the use of geoserver-rest for automation of this process. The geoserver-rest can dynamically create the SLD file based on the uploaded geospatial data. The style file can be categorized or graduated type. In the case of the raster, it will read the raster data type and get the maximum and minimum value and create the style file based on the user need but for the vector data type the user has to assign based on which column he/she wants to generate the SLD file. The generated SLD file can be linked to the specific layer to publish the new design.

The geoserver-rest has four dependencies, gdal [@gdal], pycurl [@pycurl], psycopg2 [@psycopg2] and seaborn [@seaborn]. The full documentation of the project is available in `Python Package Index` [@gsrest].

# Sample code

```python
from geo.Geoserver import Geoserver

# initialize geoserver
geo = Geoserver('http://localhost:8080/geoserver',
                username='admin',
                password='geoserver')

#create workspace
geo.create_workspace(workspace='demo')

#upload raster data: create store and layer at same time inside demo workspace
geo.create_coveragestore(lyr_name='layer1'
                          path=r'path\to\raster\file.tif',
                          workspace='demo')

#update raster data (replace the existing one)
geo.create_coveragestore(lyr_name='layer1'
                          path=r'new\path\to\raster\file.tif',
                          workspace='demo',
                          overwrite=True)

#create style file dynamically and apply it to the required layer
geo.create_coveragestyle(raster_path=r'path\to\raster\file.tiff',
                          style_name='style_1',
                          workspace='demo',
                          color_ramp='RdYiGn')
geo.publish_style(layer_name='geoserver_layer_name',
                  style_name='raster_file_name',
                  workspace='demo')

#delete layer and store
geo.delete_layer(layer_name='layer1', workspace='demo')
geo.delete_coveragestore(coveragestore_name='layer1', workspace='demo')
```

# Statement of need

Web-platforms are designed to access services or data [@Demmer:2007]. It should communicate/exchange the information through the Application Programming Interface(API) [@Cleveland:2020]. REST API is one of the best ways to circulate the data throughout the software. It should support at least GET, POST, DELETE and PUT requests. The geoserver make it easier to visualize the geospatial data in the web platform with the help of Web Map Services (WMS), Web Map and Tile Service (WMTS) and Web Feature Services (WFS). Since it is a server, proper way of data sharing is needed. The pipeline between a server and the software can help to send the request and get back the desire response [@Stefano:2017, @Colin:2014, @geoserver]. Here comes the major use of geoserver-rest for automation of data sharing between geoserver and web-platforms. Python is one of the leading technology for web development [@Taneja:2007]. Implementation of geoserver-rest in python will significantly enhance the approach of GIS application development. It makes the developer job easier to control and manage the geospatial data.

# Acknowledgements

I would like to acknowledge Er. Rabin Ojha for his valuable contribution in documentation.

# References
