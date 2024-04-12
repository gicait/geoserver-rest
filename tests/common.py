import os

from geo.Geoserver import Geoserver

GEO_URL = os.getenv("GEO_URL", "http://localhost:8080/geoserver")  # relative to test machine

geo = Geoserver(GEO_URL, username=os.getenv("GEO_USER", "admin"), password=os.getenv("GEO_PASS", "geoserver"))

postgis_params = {
    "host": os.getenv("DB_HOST", "localhost"),  # relative to the geoserver instance
    "port": os.getenv("DB_PORT", "5432"),  # relative to the geoserver instance
    "db": os.getenv("DB_NAME", "geodb"),
    "pg_user": os.getenv("DB_USER", "geodb_user"),
    "pg_password": os.getenv("DB_PASS", "geodb_pass")
}

# in case you are using docker or something, and the location of the database is different relative to your host machine
postgis_params_local_override = {
    "host": os.getenv("DB_HOST_LOCAL", "localhost"),  # relative to the test machine
    "port": os.getenv("DB_PORT_LOCAL", "5432"),  # relative to the test machine
}
postgis_params_local = {**postgis_params, **postgis_params_local_override}
