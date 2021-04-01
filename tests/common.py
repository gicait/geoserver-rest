import os

from geo.Geoserver import Geoserver

GEO_URL = os.getenv("GEO_URL", "http://localhost:8080/geoserver")

geo = Geoserver(GEO_URL, username="admin", password="geoserver")
