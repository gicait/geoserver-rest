import pycurl
import os
import io
import requests
from .Style import coverage_style_xml, outline_only_xml, catagorize_xml, classified_xml
from .Calculation_gdal import raster_value
from .supports import prepare_zip_file


# call back class for read the data
class DataProvider(object):
    def __init__(self, data):
        self.data = data
        self.finished = False

    def read_cb(self, size):
        assert len(self.data) <= size
        if not self.finished:
            self.finished = True
            return self.data
        else:
            # Nothing more to read
            return ""


# callback class for reading the files
class FileReader:
    def __init__(self, fp):
        self.fp = fp

    def read_callback(self, size):
        return self.fp.read(size)


class Geoserver:
    def __init__(self, service_url='http://localhost:8080/geoserver', username='admin', password='geoserver'):
        self.service_url = service_url
        self.username = username
        self.password = password

    def get_manifest(self):
        '''
        It returns the manifest of the geoserver
        '''
        try:
            url = '{0}/rest/about/manifest.json'.format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return ('get_manifest error: ', e)

    def get_version(self):
        '''
        It returns the version of the geoserver
        '''
        try:
            url = '{0}/rest/about/version.json'.format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return ('get_version error: ', e)

    def get_status(self):
        '''
        It returns the status of the geoserver
        '''
        try:
            url = '{0}/rest/about/status.json'.format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return ('get_status error: ', e)

    def get_system_status(self):
        '''
        It returns the system status of the geoserver
        '''
        try:
            url = '{0}/rest/about/system-status.json'.format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return ('get_system_status error: ', e)

    def reload(self):
        '''
        Reloads the GeoServer catalog and configuration from disk. This operation is used in cases where an external tool has modified the on-disk configuration. This operation will also force GeoServer to drop any internal caches and reconnect to all data stores.
        curl -X POST http://localhost:8080/geoserver/rest/reload -H  "accept: application/json" -H  "content-type: application/json"
        '''
        try:
            url = '{0}/rest/reload'.format(self.service_url)
            r = requests.post(url, auth=(self.username, self.password))
            return 'Status code: {}'.format(r.status_code)

        except Exception as e:
            return 'reload error: {}'.format(e)

    def reset(self):
        '''
        Resets all store, raster, and schema caches. This operation is used to force GeoServer to drop all caches and store connections and reconnect to each of them the next time they are needed by a request. This is useful in case the stores themselves cache some information about the data structures they manage that may have changed in the meantime.
        curl -X POST http://localhost:8080/geoserver/rest/reset -H  "accept: application/json" -H  "content-type: application/json"
        '''
        try:
            url = '{0}/rest/reset'.format(self.service_url)
            r = requests.post(url, auth=(self.username, self.password))
            return 'Status code: {}'.format(r.status_code)

        except Exception as e:
            return 'reload error: {}'.format(e)

    def get_datastore(self, store_name, workspace=None):
        '''
        data store in given workspace
        If workspace is not provided, it will take the default workspace
        curl -X GET http://localhost:8080/geoserver/rest/workspaces/demo/datastores -H  "accept: application/xml" -H  "content-type: application/json"
        '''
        try:
            if workspace == None:
                workspace = 'default'

            url = '{0}/rest/workspaces/{1}/datastores/{2}'.format(
                self.service_url, workspace, store_name)

            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_datastores error: {}".format(e)

    def get_datastores(self, workspace=None):
        '''
        List all data stores in workspace ws.
        If workspace is not provided, it will listout all the datastores inside default workspace
        curl -X GET http://localhost:8080/geoserver/rest/workspaces/demo/datastores -H  "accept: application/xml" -H  "content-type: application/json"
        '''
        try:
            if workspace == None:
                workspace = 'default'

            url = '{0}/rest/workspaces/{1}/datastores.json'.format(
                self.service_url, workspace)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_datastores error: {}".format(e)

    def get_coveragestore(self, coveragestore_name, workspace=None):
        '''
        It returns the store name if exist
        '''
        try:
            payload = {'recurse': 'true'}
            if workspace is None:
                workspace = 'default'
            url = '{0}/rest/workspaces/{1}/coveragestores/{2}.json'.format(
                self.service_url, workspace, coveragestore_name)
            r = requests.get(url, auth=(
                self.username, self.password), params=payload)
            print('Status code: {0}, Get coverage store'.format(r.status_code))

            return r.json()

        except Exception as e:
            return 'Error: {}'.format(e)

    def get_coveragestores(self, workspace=None):
        '''
        Get all the coveragestores inside specific workspace
        '''
        try:
            if workspace is None:
                workspace = 'default'

            url = '{0}/rest/workspaces/{1}/coveragestores'.format(
                self.service_url, workspace)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return 'get_coveragestores error: {}'.format(e)

    def get_layer(self, layer_name, workspace=None):
        '''
        Get the layer by layer name
        '''
        try:
            url = '{0}/rest/layers/{1}'.format(
                self.service_url, layer_name)
            if workspace is not None:
                url = '{0}/rest/workspaces/{1}/layers/{2}'.format(
                    self.service_url, workspace, layer_name)

            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return 'get_layer error: {}'.format(e)

    def get_layers(self, workspace=None):
        '''
        Get all the layers from geoserver
        If workspace is None, it will listout all the layers from geoserver
        '''
        try:
            url = '{0}/rest/layers'.format(
                self.service_url)

            if workspace is not None:
                url = '{0}/rest/workspaces/{1}/layers'.format(
                    self.service_url, workspace)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return 'get_layers error: {}'.format(e)

    def get_layergroups(self, workspace=None):
        '''
        Get all the layer groups from geoserver
        If workspace is None, it will listout all the layer groups from geoserver
        '''
        try:
            url = '{0}/rest/layergroups'.format(
                self.service_url)

            if workspace is not None:
                url = '{0}/rest/workspaces/{1}/layergroups'.format(
                    self.service_url, workspace)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return 'get_layers error: {}'.format(e)

    def get_layergroup(self, layer_name, workspace=None):
        '''
        Get the layer group by layer group name
        '''
        try:
            url = '{0}/rest/layergroups/{1}'.format(
                self.service_url, layer_name)
            if workspace is not None:
                url = '{0}/rest/workspaces/{1}/layergroups/{2}'.format(
                    self.service_url, workspace, layer_name)

            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return 'get_layer error: {}'.format(e)

    def get_style(self, style_name, workspace=None):
        '''
        Get the style by style name
        '''
        try:
            url = '{0}/rest/styles/{1}.json'.format(
                self.service_url, style_name)
            if workspace is not None:
                url = '{0}/rest/workspaces/{1}/styles/{2}.json'.format(
                    self.service_url, workspace, style_name)

            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return 'get_style error: {}'.format(e)

    def get_styles(self, workspace=None):
        '''
        Get all the styles from geoserver
        '''
        try:
            url = '{0}/rest/styles.json'.format(
                self.service_url)

            if workspace is not None:
                url = '{0}/rest/workspaces/{1}/styles.json'.format(
                    self.service_url, workspace)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return 'get_styles error: {}'.format(e)

    def get_default_workspace(self):
        '''
        Get the default workspace
        '''
        try:
            url = '{0}/rest/workspaces/default'.format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return 'get_default_workspace error: {}'.format(e)

    def get_workspaces(self):
        '''
        Get all the workspaces
        '''
        try:
            url = '{0}/rest/workspaces'.format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return 'get_workspaces error: {}'.format(e)

    def set_default_workspace(self, workspace):
        '''
        Set the default workspace
        '''
        try:
            url = '{0}/rest/workspaces/default'.format(self.service_url)
            data = "<workspace><name>{}</name></workspace>".format(workspace)
            print(url, data)
            r = requests.put(url, data, auth=(self.username, self.password), headers={
                "content-type": "text/xml"})

            if r.status_code == 200:
                return "Status code: {0}, default workspace {1} set!".format(r.status_code, workspace)

        except Exception as e:
            return 'reload error: {}'.format(e)

    def create_workspace(self, workspace):
        """
        Create a new workspace in geoserver, geoserver workspace url will be same as name of the workspace
        """
        try:
            url = '{0}/rest/workspaces'.format(self.service_url)
            data = "<workspace><name>{0}</name></workspace>".format(workspace)
            headers = {"content-type": "text/xml"}
            r = requests.post(url, data, auth=(
                self.username, self.password), headers=headers)

            if r.status_code == 201:
                return "{0} Workspace {1} created!".format(r.status_code, workspace)

            if r.status_code == 401:
                raise Exception('The workspace already exist')

            else:
                raise Exception("The workspace can not be created")

        except Exception as e:
            return 'Error: {}'.format(e)

    def get_workspace(self, workspace):
        '''
        get name  workspace if exist
        Example: curl -v -u admin:admin -XGET -H "Accept: text/xml"  http://localhost:8080/geoserver/rest/workspaces/acme.xml
        '''
        try:
            payload = {'recurse': 'true'}
            url = '{0}/rest/workspaces/{1}.json'.format(
                self.service_url, workspace)
            r = requests.get(url, auth=(
                self.username, self.password), params=payload)
            if r.status_code == 200:
                return r.json()
            else:
                return None

        except Exception as e:
            return 'Error: {}'.format(e)

    def create_coveragestore(self, path, workspace=None, lyr_name=None, file_type='GeoTIFF', content_type='image/tiff', overwrite=False):
        """
        created the coveragestore, data will uploaded to the server
        the name parameter will be the name of coveragestore (coveragestore name will be assigned as the file name incase of not providing name parameter)
        the path to the file and file_type indicating it is a geotiff, arcgrid or other raster type
        """

        # overwrite feature needs to be write again
        try:
            file_size = os.path.getsize(path)

            c = pycurl.Curl()

            if lyr_name:
                file_name = lyr_name

            else:
                file_name = os.path.basename(path)
                f = file_name.split(".")
                if len(f) > 0:
                    file_name = f[0]

            if workspace is None:
                workspace = 'default'

            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)
            file_type = file_type.lower()
            c.setopt(c.URL, '{0}/rest/workspaces/{1}/coveragestores/{2}/file.{3}?coverageName={2}'.format(
                self.service_url, workspace, file_name, file_type))
            c.setopt(pycurl.HTTPHEADER, [
                     "Content-type:{}".format(content_type)])
            c.setopt(pycurl.READFUNCTION, FileReader(
                open(path, 'rb')).read_callback)
            c.setopt(pycurl.INFILESIZE, file_size)
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()
            c.close()
        except Exception as e:
            return 'Error: {}'.format(e)

    def create_featurestore(self, store_name, workspace=None, db='postgres', host='localhost', port=5432, schema='public', pg_user='postgres', pg_password='admin', overwrite=False):
        """
        Postgis store for connecting postgres with geoserver
        After creating feature store, you need to publish it
        Input parameters:specify the store name you want to be created, the postgis database parameters including host, port, database name, schema, user and password,
        """
        try:
            if workspace is None:
                workspace = 'default'

            c = pycurl.Curl()
            # connect with geoserver
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)
            c.setopt(
                c.URL, '{0}/rest/workspaces/{1}/datastores'.format(self.service_url, workspace))
            c.setopt(pycurl.HTTPHEADER, ["Content-type: text/xml"])

            # make the connection with postgis database
            database_connection = '<dataStore>'\
                '<name>{0}</name>'\
                '<connectionParameters>'\
                '<host>{1}</host>'\
                '<port>{2}</port>'\
                '<database>{3}</database>'\
                '<schema>{4}</schema>'\
                '<user>{5}</user>'\
                '<passwd>{6}</passwd>'\
                '<dbtype>postgis</dbtype>'\
                '</connectionParameters>'\
                '</dataStore>'.format(store_name, host,
                                      port, db, schema, pg_user, pg_password)
            c.setopt(pycurl.POSTFIELDSIZE, len(database_connection))
            c.setopt(pycurl.READFUNCTION, DataProvider(
                database_connection).read_cb)

            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.perform()
            c.close()
        except Exception as e:
            return "Error:%s" % str(e)

    def create_datastore(self, name, path, workspace=None, overwrite=False):
        '''
        The path referes as path to,
            1. shapefile (.shp) file or 
            2. GeoPackage (.gpkg) file or 
            3. WFS url (http://localhost:8080/geoserver/wfs?request=GetCapabilities) or 
            4. directory containing shapefiles.

        If you have PostGIS datastore, please use create_featurestore function

        The name referes as name of the datastore
        After creating the datastore, you need to publish it by using publish_featurestore function
        '''
        if workspace is None:
            workspace = 'default'

        if path is None:
            raise Exception("You must provide a full path to the data")

        data_url = '<url>file:{0}</url>'.format(path)

        if 'http://' in path:
            data_url = '<GET_CAPABILITIES_URL>{0}</GET_CAPABILITIES_URL>'.format(
                path)

        data = '<dataStore><name>{0}</name><connectionParameters>{1}</connectionParameters></dataStore>'.format(
            name, data_url)
        headers = {"content-type": "text/xml"}

        try:
            r = None
            if overwrite:
                url = '{0}/rest/workspaces/{1}/datastores/{2}'.format(
                    self.service_url, workspace, name)
                r = requests.put(url, data, auth=(
                    self.username, self.password), headers=headers)

            else:
                url = '{0}/rest/workspaces/{1}/datastores'.format(
                    self.service_url, workspace)
                r = requests.post(url, data, auth=(
                    self.username, self.password), headers=headers)

            if r.status_code in [200, 201]:
                return "Data store created/updated successfully"

            else:
                raise Exception('datastore can not be created')

        except Exception as e:
            return "Error create_datastore: {}".format(e)

    def create_shp_datastore(self, path, store_name=None, workspace=None, file_format='shp'):
        '''
        Create the datastore for shapefile
        Path refers to the path to the zipped shapefile
        The layer name will be assigned according to the shp name
        '''
        try:
            if path is None:
                raise Exception('You must provide a full path to shapefile')

            if workspace is None:
                workspace = 'default'

            if store_name is None:
                store_name = os.path.basename(path)
                f = store_name.split('.')
                if len(f) > 0:
                    store_name = f[0]

            headers = {
                "Content-type": "application/zip",
                "Accept": "application/xml",
            }

            if isinstance(path, dict):
                path = prepare_zip_file(store_name, path)

            url = '{0}/rest/workspaces/{1}/datastores/{2}/file.{3}?filename={2}&update=overwrite'.format(
                self.service_url, workspace, store_name, file_format)

            with open(path, 'rb') as f:
                r = requests.put(url, data=f.read(), auth=(
                    self.username, self.password), headers=headers)

                if (r.status_code in [200, 201]):
                    return 'The shapefile datastore created successfully!'

                else:
                    return '{}: The shapefile datastore can not be created!'.format(r.status_code)

        except Exception as e:
            return 'Error: {}'.format(e)

    def publish_featurestore(self, store_name, pg_table, workspace=None):
        """
        Only user for postgis vector data
        input parameters: specify the name of the table in the postgis database to be published, specify the store,workspace name, and  the Geoserver user name, password and URL
        """
        try:
            if workspace is None:
                workspace = 'default'

            c = pycurl.Curl()
            layer_xml = "<featureType><name>{0}</name></featureType>".format(
                pg_table)
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)
            # connecting with the specified store in geoserver
            c.setopt(c.URL, '{0}/rest/workspaces/{1}/datastores/{2}/featuretypes'.format(
                self.service_url, workspace, store_name))
            c.setopt(pycurl.HTTPHEADER, ["Content-type: text/xml"])
            c.setopt(pycurl.POSTFIELDSIZE, len(layer_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(layer_xml).read_cb)
            c.setopt(pycurl.POST, 1)
            c.perform()
            c.close()

        except Exception as e:
            return "Error:%s" % str(e)

    def publish_featurestore_sqlview(self, name, store_name, sql, key_column=None, geom_name='geom', geom_type='Geometry', workspace=None):
        try:
            if workspace is None:
                workspace = 'default'
            c = pycurl.Curl()
            layer_xml = """<featureType>
            <name>{0}</name>
            <enabled>true</enabled>
            <namespace>
            <name>{5}</name>
            </namespace>
            <title>{0}</title>
            <srs>EPSG:4326</srs>
            <metadata>
            <entry key="JDBC_VIRTUAL_TABLE">
            <virtualTable>
            <name>{0}</name>
            <sql>{1}</sql>
            <escapeSql>true</escapeSql>
            <keyColumn>{2}</keyColumn>
            <geometry>
            <name>{3}</name>
            <type>{4}</type>
            <srid>4326</srid>
            </geometry>
            </virtualTable>
            </entry>
            </metadata>
            </featureType>""".format(name, sql, key_column, geom_name, geom_type, workspace)
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)
            c.setopt(c.URL, '{0}/rest/workspaces/{1}/datastores/{2}/featuretypes'.format(
                self.service_url, workspace, store_name))
            c.setopt(pycurl.HTTPHEADER, ["Content-type: text/xml"])
            c.setopt(pycurl.POSTFIELDSIZE, len(layer_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(layer_xml).read_cb)
            c.setopt(pycurl.POST, 1)
            c.perform()
            c.close()
        except Exception as e:
            return "Error:%s" % str(e)

    def upload_style(self, path, name=None, workspace=None, sld_version='1.0.0', overwrite=False):
        '''
        The name of the style file will be, sld_name:workspace
        This function will create the style file in a specified workspace.
        Inputs: path to the sld_file, workspace,
        '''
        try:
            if name is None:
                name = os.path.basename(path)
                f = name.split('.')
                if len(f) > 0:
                    name = f[0]

            file_size = os.path.getsize(path)
            url = '{0}/rest/workspaces/{1}/styles'.format(
                self.service_url, workspace)

            sld_content_type = 'application/vnd.ogc.sld+xml'
            if sld_version == '1.1.0' or sld_version == '1.1':
                sld_content_type = 'application/vnd.ogc.se+xml'

            if workspace is None:
                workspace = 'default'
                url = '{0}/rest/styles'.format(self.service_url)

            style_xml = "<style><name>{0}</name><filename>{1}</filename></style>".format(
                name, name+'.sld')
            # create the xml file for associated style
            c = pycurl.Curl()
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)
            c.setopt(c.URL, url)
            c.setopt(pycurl.HTTPHEADER, ['Content-type:application/xml'])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(style_xml).read_cb)

            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.perform()

            # upload the style file
            c.setopt(c.URL, '{0}/{1}'.format(url, name))
            c.setopt(pycurl.HTTPHEADER, [
                     "Content-type:{0}".format(sld_content_type)])
            c.setopt(pycurl.READFUNCTION, FileReader(
                open(path, 'rb')).read_callback)
            c.setopt(pycurl.INFILESIZE, file_size)
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()
            c.close()

        except Exception as e:
            return 'Error: {}'.format(e)

    def get_featuretypes(self, workspace=None, store_name=None):
        url = '{0}/rest/workspaces/{1}/datastores/{2}/featuretypes.json'.format(
            self.service_url, workspace, store_name)
        r = requests.get(url, auth=(self.username, self.password))
        r_dict = r.json()
        features = [i['name'] for i in r_dict['featureTypes']['featureType']]
        print('Status code: {0}, Get feature type'.format(r.status_code))

        return features

    def get_feature_attribute(self, feature_type_name, workspace=None, store_name=None):
        url = '{0}/rest/workspaces/{1}/datastores/{2}/featuretypes/{3}.json'.format(
            self.service_url, workspace, store_name, feature_type_name)
        r = requests.get(url, auth=(self.username, self.password))
        r_dict = r.json()
        attribute = [i['name']
                     for i in r_dict['featureType']['attributes']['attribute']]
        print('Status code: {0}, Get feature attribute'.format(r.status_code))

        return attribute

    def get_featurestore(self, store_name, workspace):
        url = '{0}/rest/workspaces/{1}/datastores/{2}'.format(
            self.service_url, workspace, store_name)
        r = requests.get(url, auth=(self.username, self.password))
        try:
            r_dict = r.json()
            return r_dict['dataStore']

        except Exception as e:
            return 'Error: {}'.format(e)

    def create_coveragestyle(self,  raster_path, style_name=None, workspace=None, color_ramp='RdYlGn_r', cmap_type='ramp', number_of_classes=5, overwrite=False):
        '''
        The name of the style file will be, rasterName:workspace
        This function will dynamically create the style file for raster.
        Inputs: name of file, workspace, cmap_type (two options: values, range), ncolors: determins the number of class, min for minimum value of the raster, max for the max value of raster
        '''
        try:
            raster = raster_value(raster_path)
            min = raster['min']
            max = raster['max']
            if style_name is None:
                style_name = raster['file_name']
            coverage_style_xml(color_ramp, style_name,
                               cmap_type, min, max, number_of_classes)
            style_xml = "<style><name>{0}</name><filename>{1}</filename></style>".format(
                style_name, style_name+'.sld')

            # create the xml file for associated style
            c = pycurl.Curl()
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)
            c.setopt(
                c.URL, '{0}/rest/workspaces/{1}/styles'.format(self.service_url, workspace))
            c.setopt(pycurl.HTTPHEADER, ['Content-type:text/xml'])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(style_xml).read_cb)
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.perform()

            # upload the style file
            c.setopt(c.URL, '{0}/rest/workspaces/{1}/styles/{2}'.format(
                self.service_url, workspace, style_name))
            c.setopt(pycurl.HTTPHEADER, [
                     "Content-type:application/vnd.ogc.sld+xml"])
            c.setopt(pycurl.READFUNCTION, FileReader(
                open('style.sld', 'rb')).read_callback)
            c.setopt(pycurl.INFILESIZE, os.path.getsize('style.sld'))
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()
            c.close()

            # remove temporary style created style file
            os.remove('style.sld')

        except Exception as e:
            return 'Error: {}'.format(e)

    def create_catagorized_featurestyle(self, style_name, column_name, column_distinct_values, workspace=None, color_ramp='tab20', geom_type='polygon', outline_color='#3579b1', overwrite=False):
        '''
        Dynamically create the style for postgis geometry
        The data type must be point, line or polygon
        Inputs: column_name (based on which column style should be generated), workspace,
        color_or_ramp (color should be provided in hex code or the color ramp name, geom_type(point, line, polygon), outline_color(hex_color))
        '''
        try:
            catagorize_xml(column_name, column_distinct_values,
                           color_ramp, geom_type)

            style_xml = "<style><name>{0}</name><filename>{1}</filename></style>".format(
                style_name, style_name+'.sld')

            # create the xml file for associated style
            c = pycurl.Curl()
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)
            c.setopt(
                c.URL, '{0}/rest/workspaces/{1}/styles'.format(self.service_url, workspace))
            c.setopt(pycurl.HTTPHEADER, ['Content-type:text/xml'])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(style_xml).read_cb)
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.POST, 1)
            c.perform()

            # upload the style file
            c.setopt(c.URL, '{0}/rest/workspaces/{1}/styles/{2}'.format(
                self.service_url, workspace, column_name))
            c.setopt(pycurl.HTTPHEADER, [
                     "Content-type:application/vnd.ogc.sld+xml"])
            c.setopt(pycurl.READFUNCTION, FileReader(
                open('style.sld', 'rb')).read_callback)
            c.setopt(pycurl.INFILESIZE, os.path.getsize('style.sld'))
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()
            c.close()

            # remove temporary style created style file
            os.remove('style.sld')

        except Exception as e:
            return 'Error: {}'.format(e)

    def create_outline_featurestyle(self, style_name, color='#3579b1', geom_type='polygon', workspace=None, overwrite=False):
        '''
        Dynamically create the style for postgis geometry
        The geometry type must be point, line or polygon
        Inputs: style_name (name of the style file in geoserver), workspace, color (style color)
        '''
        try:
            outline_only_xml(color, geom_type)

            style_xml = "<style><name>{0}</name><filename>{1}</filename></style>".format(
                style_name, style_name+'.sld')

            url = '{0}/rest/workspaces/{1}/styles'.format(
                self.service_url, workspace)
            if workspace is None:
                url = '{0}/rest/styles'.format(self.service_url)

            # create the xml file for associated style
            c = pycurl.Curl()
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)
            c.setopt(c.URL, url)
            c.setopt(pycurl.HTTPHEADER, ['Content-type:text/xml'])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(style_xml).read_cb)
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.perform()

            # upload the style file
            c.setopt(c.URL, '{0}/{1}'.format(url, style_name))
            c.setopt(pycurl.HTTPHEADER, [
                     "Content-type:application/vnd.ogc.sld+xml"])
            c.setopt(pycurl.READFUNCTION, FileReader(
                open('style.sld', 'rb')).read_callback)
            c.setopt(pycurl.INFILESIZE, os.path.getsize('style.sld'))
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()
            c.close()

            # remove temporary style created style file
            os.remove('style.sld')

        except Exception as e:
            return 'Error: {}'.format(e)

    def create_classified_featurestyle(self, style_name, column_name, column_distinct_values, workspace=None, color_ramp='tab20', geom_type='polygon', outline_color='#3579b1', overwrite=False):
        '''
        Dynamically create the style for postgis geometry
        The data type must be point, line or polygon
        Inputs: column_name (based on which column style should be generated), workspace,
        color_or_ramp (color should be provided in hex code or the color ramp name, geom_type(point, line, polygon), outline_color(hex_color))
        '''
        try:
            classified_xml(style_name, column_name,
                           column_distinct_values, color_ramp, geom_type='polygon')

            style_xml = "<style><name>{0}</name><filename>{1}</filename></style>".format(
                column_name, column_name+'.sld')

            # create the xml file for associated style
            c = pycurl.Curl()
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)
            c.setopt(
                c.URL, '{0}/rest/workspaces/{1}/styles'.format(self.service_url, workspace))
            c.setopt(pycurl.HTTPHEADER, ['Content-type:text/xml'])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(style_xml).read_cb)
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.POST, 1)
            c.perform()

            # upload the style file
            c.setopt(c.URL, '{0}/rest/workspaces/{1}/styles/{2}'.format(
                self.service_url, workspace, column_name))
            c.setopt(pycurl.HTTPHEADER, [
                     "Content-type:application/vnd.ogc.sld+xml"])
            c.setopt(pycurl.READFUNCTION, FileReader(
                open('style.sld', 'rb')).read_callback)
            c.setopt(pycurl.INFILESIZE, os.path.getsize('style.sld'))
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()
            c.close()

            # remove temporary style created style file
            os.remove('style.sld')

        except Exception as e:
            return 'Error: {}'.format(e)

    # def create_featurestyle()
    def publish_style(self, layer_name, style_name, workspace, content_type='text/xml'):
        """
        publishing a raster file to geoserver
        the coverage store will be created automatically as the same name as the raster layer name.
        input parameters: the parameters connecting geoserver (user,password, url and workspace name),the path to the file and file_type indicating it is a geotiff, arcgrid or other raster type
        """

        try:
            c = pycurl.Curl()
            style_xml = "<layer><defaultStyle><name>{0}</name></defaultStyle></layer>".format(
                style_name)
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)
            c.setopt(
                c.URL, '{0}/rest/layers/{1}:{2}'.format(self.service_url, workspace, layer_name))
            c.setopt(pycurl.HTTPHEADER, [
                     "Content-type: {}".format(content_type)])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(style_xml).read_cb)
            # c.setopt(pycurl.CUSTOMREQUEST, "PUT")
            c.setopt(pycurl.PUT, 1)
            c.perform()
            c.close()
        except Exception as e:
            return 'Error: {}'.format(e)

    def delete_workspace(self, workspace):
        try:
            payload = {'recurse': 'true'}
            url = '{0}/rest/workspaces/{1}'.format(self.service_url, workspace)
            r = requests.delete(url, auth=(
                self.username, self.password), param=payload)

            if r.status_code == 200:
                return('Status code: {0}, delete workspace'.format(r.status_code))

            else:
                raise Exception('Error: {1} {2}'.format(
                    r.status_code, r.content))

        except Exception as e:
            return 'Error: {}'.format(e)

    def delete_layer(self, layer_name, workspace=None):
        try:
            payload = {'recurse': 'true'}
            url = '{0}/rest/workspaces/{1}/layers/{2}'.format(
                self.service_url, workspace, layer_name)
            if workspace is None:
                url = '{0}/rest/layers/{1}'.format(
                    self.service_url, layer_name)

            r = requests.delete(url, auth=(
                self.username, self.password), params=payload)
            if r.status_code == 200:
                return('Status code: {0}, delete layer'.format(
                    r.status_code))

            else:
                raise Exception('Error: {1} {2}'.format(
                    r.status_code, r.content))

        except Exception as e:
            return 'Error: {}'.format(e)

    def delete_featurestore(self, featurestore_name, workspace):
        try:
            payload = {'recurse': 'true'}
            url = '{0}/rest/workspaces/{1}/datastores/{2}'.format(
                self.service_url, workspace, featurestore_name)
            if workspace is None:
                url = '{0}/rest/datastores/{1}'.format(
                    self.service_url, featurestore_name)
            r = requests.delete(url, auth=(
                self.username, self.password), params=payload)

            if r.status_code == 200:
                return('Status code: {0}, delete featurestore'.format(
                    r.status_code))

            else:
                raise Exception('Error: {1} {2}'.format(
                    r.status_code, r.content))

        except Exception as e:
            return 'Error: {}'.format(e)

    def delete_coveragestore(self, coveragestore_name, workspace):
        try:
            payload = {'recurse': 'true'}
            url = '{0}/rest/workspaces/{1}/coveragestores/{2}'.format(
                self.service_url, workspace, coveragestore_name)

            if workspace is None:
                url = '{0}/rest/coveragestores/{1}'.format(
                    self.service_url, coveragestore_name)

            r = requests.delete(url, auth=(
                self.username, self.password), params=payload)

            if r.status_code == 200:
                return "Coverage store deleted successfully"

            else:
                raise Exception('Error: {1} {2}'.format(
                    r.status_code, r.content))

        except Exception as e:
            return 'Error: {}'.format(e)

    def delete_style(self, style_name, workspace=None):
        try:
            payload = {'recurse': 'true'}
            url = '{0}/rest/workspaces/{1}/styles/{2}'.format(
                self.service_url, workspace, style_name)
            if workspace is None:
                url = '{0}/rest/styles/{1}'.format(
                    self.service_url, style_name)

            r = requests.delete(url, auth=(
                self.username, self.password), param=payload)

            if(r.status_code == 200):
                return ('Status code: {0}, delete style'.format(r.status_code))

            else:
                raise Exception('Error: {1} {2}'.format(
                    r.status_code, r.content))

        except Exception as e:
            return 'Error: {}'.format(e)
