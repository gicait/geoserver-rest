import os
import pathlib

import requests
import pytest
import sqlalchemy as sa

from geo.Style import catagorize_xml, classified_xml
from geo.Geoserver import GeoserverException, Geoserver

from .common import GEO_URL, geo, postgis_params, postgis_params_local

HERE = pathlib.Path(__file__).parent.resolve()


class TestCustomRequestParameters:

    def test_custom_request_parameters(self):

        """
        Tests that a custom request parameter is properly applied when spcecified

        It's a bit kludgy, we check that if we specify a timeout of 0, then requests raises a ValueError, which is the
        intended behaviour for that library given that option. That proves that the request_options are getting passed
        properly for any given request
        """

        geo = Geoserver(GEO_URL,
                        username=os.getenv("GEO_USER", "admin"),
                        password=os.getenv("GEO_PASS", "geoserver"),
                        request_options={"timeout": 0})
        url = "{}/rest/about/manifest.json".format(geo.service_url)
        with pytest.raises(ValueError):
            geo._requests("get", url)


class TestGeoserverMethods:

    def test_get_manifest(self):

        """
        Tests that the manifest endpoint returns the proper dictionary
        """

        response = geo.get_manifest()
        assert len(response["about"]) > 0

    def test_get_version(self):

        """
        Tests that the version endpoint returns a dictionary containing at least one resource called `GeoServer`
        """

        response = geo.get_version()
        assert "GeoServer" in [resource["@name"] for resource in response["about"]["resource"]]

    def test_get_status(self):

        """
        Tests that the status endpoint returns a dictionary containing a key called `status`
        """

        response = geo.get_status()
        # NOT A TYPO! Geoserver returns a key called exactly `statuss`
        assert "statuss" in response.keys()

    def test_get_system_status(self):

        """
        Tests that the status endpoint returns a dictionary containing a key called `metric`
        """

        response = geo.get_system_status()
        assert "metrics" in response.keys()

    def test_reload(self):

        """
        Tests that the reload endpoint returns the string `Status code: 200`
        """

        response = geo.reload()
        assert response == "Status code: 200"

    def test_reset(self):

        """
        Tests that the reset endpoint returns the string `Status code: 200`
        """

        response = geo.reset()
        assert response == "Status code: 200"


class TestWorkspace:

    def test_get_default_workspace(self):

        response = geo.get_default_workspace()
        # Assuming that we are using the kartoza/geoserver docker image, which uses `ne` as the default workspace
        assert response["workspace"]["name"] == "ne"

    def test_get_workspace(self):

        response = geo.get_workspace("ne")
        assert response["workspace"]["name"] == "ne"

    def test_get_workspaces(self):

        response = geo.get_workspaces()
        # Assuming that we are using the kartoza/geoserver docker image, which uses the following as workspaces
        expected_workspace_names = sorted(['cite', 'it.geosolutions', 'ne', 'nurc', 'sde', 'sf', 'tiger', 'topp'])
        for expected_workspace_name in expected_workspace_names:
            assert expected_workspace_name in [ws["name"] for ws in response["workspaces"]["workspace"]]

    def test_set_default_workspace(self):

        try:
            geo.set_default_workspace("cite")
            response = geo.get_default_workspace()
            assert response["workspace"]["name"] == "cite"
        finally:
            # Assuming that we are using the kartoza/geoserver docker image, which uses `ne` as the default workspace
            geo.set_default_workspace("ne")


@pytest.mark.skip(reason="Only setup for local testing.")
class TestRequest:
    def test_information(self):
        geo.get_version()
        geo.get_manifest()
        geo.get_status()
        geo.get_system_status()

    def test_datastore_create(self):
        a = geo.create_shp_datastore(
            r"C:\Program Files (x86)\GeoServer 2.15.1\data_dir\data\demo\C_Jamoat\C_Jamoat.zip",
            store_name="111",
        )
        # assert a == "something we expect"
        print(a)
        geo.get_layer("jamoat-db", workspace="demo")
        geo.get_datastore("111", "demo")
        geo.get_style(
            "hazard_exp",
            workspace="geoinformatics_center",
        )
        a = geo.get_styles()
        # assert a == "something we expect"

        a = geo.create_datastore(
            "datastore4",
            r"http://localhost:8080/geoserver/wfs?request=GetCapabilities",
            workspace="demo",
            overwrite=True,
        )
        # assert a == "something we expect"

        a = geo.create_shp_datastore(
            r"C:\Users\tek\Desktop\try\geoserver-rest\data\A_Admin_boundaries\A_Country\A_Country.zip",
            "aaa",
            "default",
        )
        # assert a == "something we expect"
        print(a)

        geo.publish_featurestore("datastore2", "admin_units", workspace="demo")


@pytest.mark.skip(reason="Only setup for local testing.")
class TestCoverages:
    def test_coverage(self):
        geo.create_coveragestore(
            r"C:\Users\tek\Desktop\try\geoserver-rest\data\C_EAR\a_Agriculture\agri_final_proj.tif",
            workspace="demo",
            lyr_name="name_try",
            overwrite=False,
        )
        geo.upload_style(
            r"C:\Users\tek\Desktop\try_sld.sld", sld_version="1.1.0", workspace="try"
        )
        geo.publish_style("agri_final_proj", "dem", "demo")
        color_ramp1 = {"value1": "#ffff55", "value2": "#505050", "value3": "#404040"}
        geo.create_coveragestyle(
            style_name="demo",
            raster_path=r"C:\Users\tek\Desktop\try\geoserver-rest\data\flood_alert.tif",
            workspace="demo",
            color_ramp=color_ramp1,
            cmap_type="values",
            overwrite=True,
        )


# @pytest.mark.skip(reason="Only setup for local testing.")
class TestFeatures:

    def test_featurestore(self):

        """
        Tests that you can publish an existing table as a layer
        """

        table_name = "test_table"
        workspace_name = "test_ws"
        featurestore_name = "test_ds"

        # set up DB and create a table with a feature inside
        DB_HOST = postgis_params_local["host"]
        DB_PORT = postgis_params_local["port"]
        DB_PASS = postgis_params_local["pg_password"]
        DB_USER = postgis_params_local["pg_user"]
        DB_NAME = postgis_params_local["db"]
        engine = sa.create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}", echo=False)
        with engine.connect() as conn:
            conn.execute(sa.text(f"drop table if exists {table_name};"))
            conn.execute(sa.text(f"create table {table_name} (id integer primary key, foo text, geom geometry);"))
            conn.execute(sa.text(f"insert into {table_name} (id, foo, geom) values (0, 'bar', ST_MakePoint(0, 0, 4326));"))
            conn.commit()

        try:
            geo.create_workspace(workspace_name)
            geo.create_featurestore(workspace=workspace_name, store_name=featurestore_name, **postgis_params)
            geo.publish_featurestore(store_name=featurestore_name, pg_table=table_name, workspace=workspace_name)

            wfs_query = f"{GEO_URL}/{workspace_name}/ows?" \
                        "service=WFS&" \
                        "version=1.0.0&" \
                        "request=GetFeature&" \
                        f"typeName={workspace_name}%3A{table_name}&" \
                        "outputFormat=application%2Fjson"

            r = requests.get(wfs_query)
            assert r.status_code == 200

            data = r.json()
            assert data["features"][0]["properties"]["foo"] == "bar"

        finally:
            with engine.connect() as conn:
                conn.execute(sa.text(f"drop table {table_name};"))
            geo.delete_workspace(workspace_name)

    def test_sql_featurestore(self):

        """
        Tests that you publish an SQL query as a layer
        """

        workspace_name = "test_ws"
        featurestore_name = "test_ds"
        sqlview_name = "test_sqlview"
        sqlview_key_column = "id"
        sqlview_geom_column = "geom"
        sqlview_query = f"select 0 as {sqlview_key_column}, 'bar' as foo, ST_MakePoint(0, 0, 4326) as {sqlview_geom_column}"
        wfs_query = f"{GEO_URL}/{workspace_name}/ows?" \
                    "service=WFS&" \
                    "version=1.0.0&" \
                    "request=GetFeature&" \
                    f"typeName={workspace_name}%3A{sqlview_name}&" \
                    "outputFormat=application%2Fjson"

        try:
            geo.create_workspace(workspace_name)
            geo.create_featurestore(workspace=workspace_name, store_name=featurestore_name, **postgis_params)
            geo.publish_featurestore_sqlview(
                name=sqlview_name,
                store_name=featurestore_name,
                sql=sqlview_query,
                workspace=workspace_name,
                key_column=sqlview_key_column
            )

            r = requests.get(wfs_query)
            assert r.status_code == 200

            data = r.json()
            assert data["features"][0]["properties"]["foo"] == "bar"

        finally:
            geo.delete_workspace(workspace_name)

    def test_parameterized_sql_featurestore(self):

        """
        Tests that you can publish a parameterized SQL query as a layer
        """

        workspace_name = "test_ws"
        featurestore_name = "test_ds"
        sqlview_name = "test_parameterized_sqlview"
        sqlview_key_column = "id"
        sqlview_geom_column = "geom"
        foo_default_val = "bar"
        foo_parameterized_value = "baz"
        parameters = [{"name": "foo", "defaultValue": foo_default_val}]
        sqlview_query = f"select 0 as {sqlview_key_column}, '%foo%' as foo, ST_MakePoint(0, 0, 4326) as {sqlview_geom_column}"
        wfs_query = f"{GEO_URL}/{workspace_name}/ows?" \
                    "service=WFS&" \
                    "version=1.0.0&" \
                    "request=GetFeature&" \
                    f"typeName={workspace_name}%3A{sqlview_name}&" \
                    "outputFormat=application%2Fjson"

        try:
            geo.create_workspace(workspace_name)
            geo.create_featurestore(workspace=workspace_name, store_name=featurestore_name, **postgis_params)
            geo.publish_featurestore_sqlview(
                name=sqlview_name,
                store_name=featurestore_name,
                sql=sqlview_query,
                workspace=workspace_name,
                key_column=sqlview_key_column,
                parameters=parameters
            )

            # test without specifying param (should return default value)
            r = requests.get(wfs_query)
            assert r.status_code == 200
            data = r.json()
            assert data["features"][0]["properties"]["foo"] == foo_default_val

            # test with specifying param
            wfs_query += f"&viewparams=foo:{foo_parameterized_value}"
            r = requests.get(wfs_query)
            assert r.status_code == 200
            data = r.json()
            assert data["features"][0]["properties"]["foo"] == foo_parameterized_value

        finally:
            geo.delete_workspace(workspace_name)

    def test_parameterized_sql_featurestore_regexp_validator(self):

        """
        Tests that the parameterized SQL view layer's logic for handling regular expressing validators works as expected
        """

        workspace_name = "test_ws"
        featurestore_name = "test_ds"
        sqlview_name = "test_parameterized_sqlview"
        sqlview_key_column = "id"
        sqlview_geom_column = "geom"
        parameters = [{"name": "foo", "defaultValue": "baz"},
                      {"name": "bar", "defaultValue": "baz-", "regexpValidator": "^[\\w\\d\\s\\-]+$"}]
        sqlview_query = f"select 0 as {sqlview_key_column}, '%foo%' as foo, '%bar%' as bar, ST_MakePoint(0, 0, 4326) as {sqlview_geom_column}"

        try:
            geo.create_workspace(workspace_name)
            geo.create_featurestore(workspace=workspace_name, store_name=featurestore_name, **postgis_params)
            geo.publish_featurestore_sqlview(
                name=sqlview_name,
                store_name=featurestore_name,
                sql=sqlview_query,
                workspace=workspace_name,
                key_column=sqlview_key_column,
                parameters=parameters
            )

            # test that adding a hyphen to foo fails because the default regexp validator forbids it
            wfs_query = f"{GEO_URL}/{workspace_name}/ows?" \
                        "service=WFS&" \
                        "version=1.0.0&" \
                        "request=GetFeature&" \
                        f"typeName={workspace_name}%3A{sqlview_name}&" \
                        "outputFormat=application%2Fjson&" \
                        f"viewparams=foo:baz-"

            r = requests.get(wfs_query)
            # regexp validator failure still returns 200, but resultant XML indicates a Java exception
            assert r.status_code == 200
            assert "java.io.IOExceptionInvalid value for parameter foo" in r.text

            # test that adding a hyphen to bar succeeds because the custom regexp validator allows it
            wfs_query = f"{GEO_URL}/{workspace_name}/ows?" \
                        "service=WFS&" \
                        "version=1.0.0&" \
                        "request=GetFeature&" \
                        f"typeName={workspace_name}%3A{sqlview_name}&" \
                        "outputFormat=application%2Fjson&" \
                        f"viewparams=bar:baz-"

            wfs_query += f"&viewparams=bar:baz-"
            r = requests.get(wfs_query)
            assert r.status_code == 200
            data = r.json()
            assert data["features"][0]["properties"]["bar"] == "baz-"

        finally:
            geo.delete_workspace(workspace_name)

    def test_parameterized_sql_featurestore_fails_when_integer_parameter_has_no_default_value(self):

        """
        Tests that a non-string parameter in a parameterized sql view raises a descriptive error. This problem is not
        very well documented in Geoserver but is clearly reproducible.
        """

        workspace_name = "test_ws"
        featurestore_name = "test_ds"
        sqlview_name = "test_sqlview"
        sqlview_key_column = "id"
        sqlview_geom_column = "geom"

        sqlview_query = f"""
            with comparator as (
                select 0 as id, ST_MakePoint(0, 0, 4326) as {sqlview_geom_column}
            )
            
            select
                c.id as {sqlview_key_column},
                c.geom as {sqlview_geom_column}
            from
                comparator c
            where
                c.id = %foo%
        """

        parameters = [{"name": "foo"}]

        try:
            geo.create_workspace(workspace_name)
            geo.create_featurestore(workspace=workspace_name, store_name=featurestore_name, **postgis_params)

            with pytest.raises(ValueError):
                geo.publish_featurestore_sqlview(
                    name=sqlview_name,
                    store_name=featurestore_name,
                    sql=sqlview_query,
                    workspace=workspace_name,
                    parameters=parameters
                )
            pass

        finally:
            geo.delete_workspace(workspace_name)


@pytest.mark.skip(reason="Only setup for local testing.")
class TestStyles:
    def test_styles(self):
        geo.create_outline_featurestyle(
            "demo", geom_type="polygon", workspace="demo", overwrite=True
        )
        catagorize_xml(
            "kamal", [1, 2, 3, 4, 5, 6, 7], num_of_class=30, geom_type="line"
        )
        geo.create_catagorized_featurestyle(
            "kamal2", [1, 2, 3, 4, 5, 6, 7], workspace="demo"
        )


@pytest.mark.skip("Doesn't work for some reason")
class TestCreateGeopackageDatastore:

    def test_create_geopackage_datastore_from_file(self):

        geo.create_gpkg_datastore(f"{HERE}/data/countries-test.gpkg")
        store = geo.get_datastore("countries-test")
        layer = geo.get_layer("countries-test")
        assert store["dataStore"]["name"] == "countries-test"
        assert layer["layer"]["name"] == "countries-test"


class TestUploadStyles:

    def test_upload_style_from_file(self):

        try:
            geo.delete_style("test_upload_style")
        except GeoserverException:
            pass

        geo.upload_style(f"{HERE}/data/style.sld", "test_upload_style")
        style = geo.get_style("test_upload_style")
        assert style["style"]["name"] == "test_upload_style"

    def test_upload_style_from_malformed_file_fails(self):

        try:
            geo.delete_style("style_doesnt_exist")
        except GeoserverException:
            pass

        with pytest.raises(ValueError):
            geo.upload_style(f"{HERE}/data/style_doesnt_exist.sld", "style_doesnt_exist")
        with pytest.raises(GeoserverException):
            style = geo.get_style("style_doesnt_exist")
            print()

    def test_upload_style_from_xml(self):

        try:
            geo.delete_style("test_upload_style")
        except GeoserverException:
            pass

        xml = open(f"{HERE}/data/style.sld").read()
        geo.upload_style(xml, "test_upload_style")
        style = geo.get_style("test_upload_style")
        assert style["style"]["name"] == "test_upload_style"

    def test_upload_style_from_malformed_xml_fails(self):

        try:
            geo.delete_style("style_malformed")
        except GeoserverException:
            pass

        xml = open(f"{HERE}/data/style.sld").read()[1:]
        with pytest.raises(ValueError):
            geo.upload_style(xml, "style_malformed")
        with pytest.raises(GeoserverException):
            style = geo.get_style("style_malformed")


@pytest.mark.skip(reason="Only setup for local testing.")
class TestPostGres:
    # from geo.Postgres import Db

    # pg = Db(dbname="postgres", user="postgres", password="admin", host="localhost")

    def test_postgres(self):
        print(self.pg.get_columns_names("zones"))
        # assert self.pg.get_columns_names("zones") == "something we expect"
        print(self.pg.get_all_values("zones", "shape_area"))
        # assert self.pg.get_columns_names("zones") == "something we expect"
        self.pg.create_schema("kamal kshetri")
        a = self.pg.get_columns_names("jamoat-db")
        print(a)
        # assert a == "something we expect"
        a = self.pg.get_all_values("jamoat-db", "shape_area")[5]
        print(a)
        # assert a == "something we expect"


@pytest.mark.skip(reason="Only setup for local testing.")
class TestDeletion:
    # There needs to be a setup here first before we can delete anything

    def test_delete(self):
        geo.delete_workspace(workspace="demo")
        geo.delete_layer(layer_name="agri_final_proj", workspace="demo")
        geo.delete_featurestore(featurestore_name="feature_store", workspace="demo")
        geo.delete_coveragestore(coveragestore_name="store_name", workspace="demo")
        geo.delete_style(style_name="kamal2", workspace="demo")


class TestOther:
    def test_classified_xml(self):
        classified_xml("test", "kamal", [4, 5, 3, 12], color_ramp="hot")
