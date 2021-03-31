from geo.Geoserver import Geoserver
import os

GEO_URL = os.getenv("GEO_URL", "http://localhost:8080/geoserver")

geo = Geoserver(
    GEO_URL, username="admin", password="geoserver"
)
