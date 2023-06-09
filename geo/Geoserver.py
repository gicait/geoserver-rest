import os
from typing import Optional

import pycurl
import requests

from .Calculation_gdal import raster_value
from .Style import catagorize_xml, classified_xml, coverage_style_xml, outline_only_xml
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
    """
    Attributes
    ----------
    service_url : str
        The URL for the GeoServer instance.
    username : str
        Login name for session.
    password: str
        Password for session.
    """

    def __init__(
        self,
        service_url="http://localhost:8080/geoserver",
        username="admin",
        password="geoserver",
    ):
        self.service_url = service_url
        self.username = username
        self.password = password

    def get_manifest(self):
        """
        Returns the manifest of the geoserver.
        """
        try:
            url = "{}/rest/about/manifest.json".format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_manifest error: ", e

    def get_version(self):
        """
        Returns the version of the geoserver.
        """
        try:
            url = "{}/rest/about/version.json".format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_version error: ", e

    def get_status(self):
        """
        Returns the status of the geoserver.
        """
        try:
            url = "{}/rest/about/status.json".format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_status error: ", e

    def get_system_status(self):
        """
        It returns the system status of the geoserver
        """
        try:
            url = "{}/rest/about/system-status.json".format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_system_status error: ", e

    def reload(self):
        """
        Reloads the GeoServer catalog and configuration from disk.

        This operation is used in cases where an external tool has modified the on-disk configuration.
        This operation will also force GeoServer to drop any internal caches and reconnect to all data stores.
        curl -X POST http://localhost:8080/geoserver/rest/reload -H  "accept: application/json" -H  "content-type: application/json"
        """
        try:
            url = "{}/rest/reload".format(self.service_url)
            r = requests.post(url, auth=(self.username, self.password))
            return "Status code: {}".format(r.status_code)

        except Exception as e:
            return "reload error: {}".format(e)

    def reset(self):
        """
        Resets all store, raster, and schema caches. This operation is used to force GeoServer to drop all caches and
        store connections and reconnect to each of them the next time they are needed by a request. This is useful in
        case the stores themselves cache some information about the data structures they manage that may have changed
        in the meantime.
        curl -X POST http://localhost:8080/geoserver/rest/reset -H  "accept: application/json" -H  "content-type: application/json"
        """
        try:
            url = "{}/rest/reset".format(self.service_url)
            r = requests.post(url, auth=(self.username, self.password))
            return "Status code: {}".format(r.status_code)

        except Exception as e:
            return "reload error: {}".format(e)

    def get_datastore(self, store_name: str, workspace: Optional[str] = None):
        """
        Return the data store in a given workspace.

        If workspace is not provided, it will take the default workspace
        curl -X GET http://localhost:8080/geoserver/rest/workspaces/demo/datastores -H  "accept: application/xml" -H  "content-type: application/json"
        """
        try:
            if workspace is None:
                workspace = "default"

            url = "{}/rest/workspaces/{}/datastores/{}".format(
                self.service_url, workspace, store_name
            )

            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_datastores error: {}".format(e)

    def get_datastores(self, workspace: Optional[str] = None):
        """
        List all data stores in a workspace.

        If workspace is not provided, it will listout all the datastores inside default workspace
        curl -X GET http://localhost:8080/geoserver/rest/workspaces/demo/datastores -H  "accept: application/xml" -H  "content-type: application/json"
        """
        try:
            if workspace is None:
                workspace = "default"

            url = "{}/rest/workspaces/{}/datastores.json".format(
                self.service_url, workspace
            )
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_datastores error: {}".format(e)

    def get_coveragestore(
        self, coveragestore_name: str, workspace: Optional[str] = None
    ):
        """
        Returns the store name if it exists.
        """
        try:
            payload = {"recurse": "true"}
            if workspace is None:
                workspace = "default"
            url = "{}/rest/workspaces/{}/coveragestores/{}.json".format(
                self.service_url, workspace, coveragestore_name
            )
            r = requests.get(url, auth=(self.username, self.password), params=payload)
            print("Status code: {}, Get coverage store".format(r.status_code))

            return r.json()

        except Exception as e:
            return "Error: {}".format(e)

    def get_coveragestores(self, workspace: str = None):
        """
        Returns all the coveragestores inside a specific workspace.
        """
        try:
            if workspace is None:
                workspace = "default"

            url = "{}/rest/workspaces/{}/coveragestores".format(
                self.service_url, workspace
            )
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_coveragestores error: {}".format(e)

    def get_layer(self, layer_name: str, workspace: Optional[str] = None):
        """
        Returns the layer by layer name.
        """
        try:
            url = "{}/rest/layers/{}".format(self.service_url, layer_name)
            if workspace is not None:
                url = "{}/rest/workspaces/{}/layers/{}".format(
                    self.service_url, workspace, layer_name
                )

            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_layer error: {}".format(e)

    def get_layers(self, workspace: Optional[str] = None):
        """
        Get all the layers from geoserver
        If workspace is None, it will listout all the layers from geoserver
        """
        try:
            url = "{}/rest/layers".format(self.service_url)

            if workspace is not None:
                url = "{}/rest/workspaces/{}/layers".format(self.service_url, workspace)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_layers error: {}".format(e)

    def get_layergroups(self, workspace: Optional[str] = None):
        """
        Returns all the layer groups from geoserver.

        Notes
        -----
        If workspace is None, it will list all the layer groups from geoserver.
        """
        try:
            url = "{}/rest/layergroups".format(self.service_url)

            if workspace is not None:
                url = "{}/rest/workspaces/{}/layergroups".format(
                    self.service_url, workspace
                )
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_layers error: {}".format(e)

    def get_layergroup(self, layer_name: str, workspace: Optional[str] = None):
        """
        Returns the layer group by layer group name.
        """
        try:
            url = "{}/rest/layergroups/{}".format(self.service_url, layer_name)
            if workspace is not None:
                url = "{}/rest/workspaces/{}/layergroups/{}".format(
                    self.service_url, workspace, layer_name
                )

            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_layer error: {}".format(e)

    def get_style(self, style_name, workspace: Optional[str] = None):
        """
        Returns the style by style name.
        """
        try:
            url = "{}/rest/styles/{}.json".format(self.service_url, style_name)
            if workspace is not None:
                url = "{}/rest/workspaces/{}/styles/{}.json".format(
                    self.service_url, workspace, style_name
                )

            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_style error: {}".format(e)

    def get_styles(self, workspace: Optional[str] = None):
        """
        Returns all loaded styles from geoserver.
        """
        try:
            url = "{}/rest/styles.json".format(self.service_url)

            if workspace is not None:
                url = "{}/rest/workspaces/{}/styles.json".format(
                    self.service_url, workspace
                )
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_styles error: {}".format(e)

    def get_default_workspace(self):
        """
        Returns the default workspace.
        """
        try:
            url = "{}/rest/workspaces/default".format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_default_workspace error: {}".format(e)

    def get_workspaces(self):
        """
        Returns all the workspaces.
        """
        try:
            url = "{}/rest/workspaces".format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_workspaces error: {}".format(e)

    def set_default_workspace(self, workspace: str):
        """
        Set the default workspace.
        """
        try:
            url = "{}/rest/workspaces/default".format(self.service_url)
            data = "<workspace><name>{}</name></workspace>".format(workspace)
            print(url, data)
            r = requests.put(
                url,
                data,
                auth=(self.username, self.password),
                headers={"content-type": "text/xml"},
            )

            if r.status_code == 200:
                return "Status code: {}, default workspace {} set!".format(
                    r.status_code, workspace
                )

        except Exception as e:
            raise e

    def create_workspace(self, workspace: str):
        """
        Create a new workspace in geoserver.

        The geoserver workspace url will be same as the name of the workspace.
        """
        try:
            url = "{}/rest/workspaces".format(self.service_url)
            data = "<workspace><name>{}</name></workspace>".format(workspace)
            headers = {"content-type": "text/xml"}
            r = requests.post(
                url, data, auth=(self.username, self.password), headers=headers
            )

            if r.status_code == 201:
                return "{} Workspace {} created!".format(r.status_code, workspace)

            if r.status_code == 401:
                raise Exception("The workspace already exist")

            else:
                raise Exception("The workspace can not be created")

        except Exception as e:
            raise e

    def upsert_workspaces_rules(self, workspacePattern: str = '*', permission: str = 'r', role: str = None, mode: str = 'R'):
        """
        Create a new security rule for either all workspaces or a subset of them based on the 
        provided pattern, or update an existing security rule if it already exists.
        Every rule accepts multiple roles, and one role could be set in more than one rule.

        Parameters
        ----------
        workspacePattern : str
            Workspace pattern. Apply the security rule to either all workspaces (using *) or 
            a subset of them where the pattern matches (contains) the workspace name.
        permission : str
            [r|w|a] is a placeholder for the permission type. 
            r read-only access, w write access, and a indicates full (read and write) access.
        role : str
            Role name
        mode : str
            Update mode, defines how to update the rol. R Replace existing role, A Add role, D Delete rol
        """

        if role is None:
            raise Exception("You must provide a role name")

        workspacesRawData = self.get_workspaces()

        if workspacesRawData is None:
            raise Exception("There are no workspaces available")

        workspaceList = workspacesRawData['workspaces']['workspace']

        if workspacePattern != '*':
            workspaceList = [
                workspace for workspace in workspaceList if workspacePattern in workspace['name']]

        if len(workspaceList) == 0:
            raise Exception("The pattern does not match any workspace")

        created = 0
        updated = 0
        deleted = 0

        rulesList = self.get_layer_rules()

        for workspace in workspaceList:
            try:
                if mode != "D":
                    self.create_layer_rule(workspace['name'], '*', permission, role)
                    created += 1
                else:
                    error_data = {
                        'status_code': 409,
                    }
                    raise Exception(
                        "It is not possible to create a rule in Delete mode", error_data)
            except Exception as create_exception:
                message, error_data = create_exception.args
                status_code = error_data['status_code']
                rule = workspace['name'] + '.' + '*' + '.' + permission
                prevRole = rulesList.get(rule, None)
                newRole = role

                if prevRole is None:
                    continue

                if mode == "A":
                    if prevRole != role:
                        newRole = ",".join([prevRole, role])
                elif mode == "D":
                    if role == prevRole:
                        self.delete_layer_rule(rule)
                        deleted += 1
                        continue
                    elif role + "," in prevRole:
                        newRole = prevRole.replace(role + ",", "")
                    elif "," + role in prevRole:
                        newRole = prevRole.replace("," + role, "")
                    else:
                        continue

                if status_code == 409:
                    try:
                        self.update_layer_rule(
                            workspace['name'], '*', permission, newRole)
                        updated += 1
                    except Exception as update_exception:
                        print(
                            f"Failed to update rule for Workspace: {workspace['name']} | Error: {str(update_exception)}")
        return "Rules created: {} | Rules updated: {} | Rules deleted: {}".format(created, updated, deleted)

    def create_layer_rule(self, workspace: str, layer: str, permission: str, role: str):
        """
        Create or update a security rule for the specified layer(s) within a workspace

        Parameters
        ----------
        workspace : str
            workspace name
        layer : str,
            layer name or * for all layers within the selected workspace
        permission : str
            [r|w| ] is a placeholder for the permission type. 
            r read-only access, w write access and a indicates full (read and write) access.
        role : str
            rol name

        Example: curl -v -u admin:geoserver -XPOST http://localhost:8080/geoserver/rest/security/acl/layers -H "accept: application/json" -H "content-type: application/xml" -d "<rules><rule resource=\"WORKSPACE_NAME.*.r\">ROL_NAME</rule></rules>"
        """
        try:
            url = "{}/rest/security/acl/layers".format(self.service_url)
            data = "<rules><rule resource='{}.{}.{}'>{}</rule></rules>".format(
                workspace, layer, permission, role)
            headers = {"content-type": "application/xml"}
            r = requests.post(
                url, data, auth=(self.username, self.password), headers=headers
            )

            if r.status_code == 200:
                return "{} Rule created! Workspace: {} | Layer: {} | Permission: {} | Role: {} ".format(r.status_code, workspace, layer, permission, role)

            if r.status_code == 409:
                error_data = {
                    'status_code': r.status_code,
                }
                raise Exception("The rule already exists!", error_data)

            else:
                raise Exception("The rule can not be created")

        except Exception as e:
            raise e

    def update_layer_rule(self, workspace: str, layer: str, permission: str, role: str):
        """
        Update a current security rule for the specified layer(s) within a workspace

        Parameters
        ----------
        workspace : str
            workspace name
        layer : str,
            layer name or * for all layers within the selected workspace
        permission : str
            [r|w|a] is a placeholder for the permission type. 
            r read-only access, w write access and a indicates full (read and write) access.
        role : str
            rol name

        Example: curl -v -u admin:geoserver -XPUT http://localhost:8080/geoserver/rest/security/acl/layers -H "accept: application/json" -H "content-type: application/xml" -d "<rules><rule resource=\"WORKSPACE_NAME.*.r\">ROL_NAME</rule></rules>"
        """
        try:
            url = "{}/rest/security/acl/layers".format(self.service_url)
            data = "<rules><rule resource='{}.{}.{}'>{}</rule></rules>".format(
                workspace, layer, permission, role)
            headers = {"content-type": "application/xml"}
            r = requests.put(
                url, data, auth=(self.username, self.password), headers=headers
            )
            if r.status_code == 200:
                return "{} Rule updated! Workspace: {} | Layer: {} | Permission: {} | Role: {} ".format(r.status_code, workspace, layer, permission, role)

            if r.status_code == 409:
                raise Exception("The rule can not be updated because it does not exist")

            else:
                raise Exception("The rule can not be updated")

        except Exception as e:
            raise e

    def delete_layer_rule(self, rule: str = None):
        """
        Delete a specific layer rule
        Parameters
        ----------
        role : str
            single rule to be deleted. Must be in the format: <workspace>.<layer>.<permission>
        """

        if rule is None:
            raise Exception("You must provide a rule")

        try:
            url = "{}/rest/security/acl/layers/{}".format(self.service_url, rule)
            r = requests.delete(url, auth=(self.username, self.password))
            if r.status_code == 200:
                return "{} Rule deleted! Rule: {}".format(r.status_code, rule)
            else:
                return None

        except Exception as e:
            return "Error: {}".format(e)

    def get_layer_rules(self):
        """
        Get all layer rules
        """
        try:
            url = "{}/rest/security/acl/layers.json".format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            if r.status_code == 200:
                return r.json()
            else:
                return None

        except Exception as e:
            return "Error: {}".format(e)

    def get_workspace(self, workspace: str):
        """
        Get workspace name if it exists.

        Example: curl -v -u admin:admin -XGET -H "Accept: text/xml"  http://localhost:8080/geoserver/rest/workspaces/acme.xml
        """
        try:
            payload = {"recurse": "true"}
            url = "{}/rest/workspaces/{}.json".format(self.service_url, workspace)
            r = requests.get(url, auth=(self.username, self.password), params=payload)
            if r.status_code == 200:
                return r.json()
            else:
                return None

        except Exception as e:
            return "Error: {}".format(e)

    def create_coveragestore(
        self,
        path,
        workspace: Optional[str] = None,
        layer_name: Optional[str] = None,
        file_type: str = "GeoTIFF",
        content_type: str = "image/tiff",
        overwrite: bool = False,
    ):
        """
        Creates the coveragestore; Data will uploaded to the server.

        Parameters
        ----------
        path : str
        workspace : str, optional
        layer_name : str, optional
            The name of coveragestore. If not provided, parsed from the file name.
        file_type : str
        content_type : str
        overwrite : bool

        Notes
        -----
        the path to the file and file_type indicating it is a geotiff, arcgrid or other raster type
        """

        # overwrite feature needs to be write again
        c = pycurl.Curl()
        try:
            file_size = os.path.getsize(path)

            if layer_name:
                file_name = layer_name

            else:
                file_name = os.path.basename(path)
                f = file_name.split(".")
                if len(f) > 0:
                    file_name = f[0]

            if workspace is None:
                workspace = "default"

            c.setopt(pycurl.USERPWD, self.username + ":" + self.password)
            file_type = file_type.lower()
            c.setopt(
                c.URL,
                "{0}/rest/workspaces/{1}/coveragestores/{2}/file.{3}?coverageName={2}".format(
                    self.service_url, workspace, file_name, file_type
                ),
            )
            c.setopt(pycurl.HTTPHEADER, ["Content-type:{}".format(content_type)])
            c.setopt(pycurl.READFUNCTION, FileReader(open(path, "rb")).read_callback)
            c.setopt(pycurl.INFILESIZE, file_size)
            if overwrite or file_type != 'imagemosaic':
                c.setopt(pycurl.CUSTOMREQUEST, "PUT")
            else:
                c.setopt(pycurl.CUSTOMREQUEST, "POST")
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()

            if c.getinfo(pycurl.HTTP_CODE) != 201:
                raise Exception(
                    f'Error code from Geoserver {c.getinfo(pycurl.RESPONSE_CODE)}')
        except Exception as e:
            raise e
        finally:
            c.close()

    def create_featurestore(
        self,
        store_name: str,
        workspace: Optional[str] = None,
        db: str = "postgres",
        host: str = "localhost",
        port: int = 5432,
        schema: str = "public",
        pg_user: str = "postgres",
        pg_password: str = "admin",
        overwrite: bool = False,
    ):
        """
        Create PostGIS store for connecting postgres with geoserver.

        Parameters
        ----------
        store_name : str
        workspace : str, optional
        db : str
        host : str
        port : int
        schema : str
        pg_user : str
        pg_password : str
        overwrite : bool

        Notes
        -----
        After creating feature store, you need to publish it.
        """
        try:
            if workspace is None:
                workspace = "default"

            c = pycurl.Curl()
            # connect with geoserver
            c.setopt(pycurl.USERPWD, self.username + ":" + self.password)
            c.setopt(
                c.URL,
                "{}/rest/workspaces/{}/datastores".format(self.service_url, workspace),
            )
            c.setopt(pycurl.HTTPHEADER, ["Content-type: text/xml"])

            # make the connection with postgis database
            database_connection = (
                "<dataStore>"
                "<name>{}</name>"
                "<connectionParameters>"
                "<host>{}</host>"
                "<port>{}</port>"
                "<database>{}</database>"
                "<schema>{}</schema>"
                "<user>{}</user>"
                "<passwd>{}</passwd>"
                "<dbtype>postgis</dbtype>"
                "</connectionParameters>"
                "</dataStore>".format(
                    store_name, host, port, db, schema, pg_user, pg_password
                )
            )
            c.setopt(pycurl.POSTFIELDSIZE, len(database_connection))
            c.setopt(pycurl.READFUNCTION, DataProvider(database_connection).read_cb)

            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.perform()
            c.close()
        except Exception as e:
            raise e

    def create_datastore(
        self,
        name: str,
        path: str,
        workspace: Optional[str] = None,
        overwrite: bool = False,
    ):
        """
        Create a datastore within the GeoServer.

        Parameters
        ----------
        name : str
            Name of datastore to be created.
            After creating the datastore, you need to publish it by using publish_featurestore function.
        path : str
            Path to shapefile (.shp) file, GeoPackage (.gpkg) file, WFS url
            (e.g. http://localhost:8080/geoserver/wfs?request=GetCapabilities) or directory containing shapefiles.
        workspace : str, optional
            Default: "default".
        overwrite : bool

        Notes
        -----
        If you have PostGIS datastore, please use create_featurestore function
        """
        if workspace is None:
            workspace = "default"

        if path is None:
            raise Exception("You must provide a full path to the data")

        data_url = "<url>file:{}</url>".format(path)

        if "http://" in path:
            data_url = "<GET_CAPABILITIES_URL>{}</GET_CAPABILITIES_URL>".format(path)

        data = "<dataStore><name>{}</name><connectionParameters>{}</connectionParameters></dataStore>".format(
            name, data_url
        )
        headers = {"content-type": "text/xml"}

        try:
            if overwrite:
                url = "{}/rest/workspaces/{}/datastores/{}".format(
                    self.service_url, workspace, name
                )
                r = requests.put(
                    url, data, auth=(self.username, self.password), headers=headers
                )

            else:
                url = "{}/rest/workspaces/{}/datastores".format(
                    self.service_url, workspace
                )
                r = requests.post(
                    url, data, auth=(self.username, self.password), headers=headers
                )

            if r.status_code in [200, 201]:
                return "Data store created/updated successfully"

            else:
                raise Exception("datastore can not be created")

        except Exception as e:
            raise e

    def create_shp_datastore(
        self,
        path: str,
        store_name: Optional[str] = None,
        workspace: Optional[str] = None,
        file_extension: str = "shp",
    ):
        """
        Create datastore for a shapefile.

        Parameters
        ----------
        path : str
            Path to the zipped shapefile (.shp).
        store_name : str, optional
            Name of store to be created. If None, parses from the filename stem.
        workspace: str, optional
            Name of workspace to be used. Default: "default".
        file_extension : str

        Notes
        -----
        The layer name will be assigned according to the shp name
        """
        try:
            if path is None:
                raise Exception("You must provide a full path to shapefile")

            if workspace is None:
                workspace = "default"

            if store_name is None:
                store_name = os.path.basename(path)
                f = store_name.split(".")
                if len(f) > 0:
                    store_name = f[0]

            headers = {
                "Content-type": "application/zip",
                "Accept": "application/xml",
            }

            if isinstance(path, dict):
                path = prepare_zip_file(store_name, path)

            url = "{0}/rest/workspaces/{1}/datastores/{2}/file.{3}?filename={2}&update=overwrite".format(
                self.service_url, workspace, store_name, file_extension
            )

            with open(path, "rb") as f:
                r = requests.put(
                    url,
                    data=f.read(),
                    auth=(self.username, self.password),
                    headers=headers,
                )

                if r.status_code in [200, 201]:
                    return "The shapefile datastore created successfully!"

                else:
                    return "{}: The shapefile datastore can not be created!".format(
                        r.status_code
                    )

        except Exception as e:
            raise e

    def publish_featurestore(
        self, store_name: str, pg_table: str, workspace: Optional[str] = None
    ):
        """

        Parameters
        ----------
        store_name : str
        pg_table : str
        workspace : str, optional

        Returns
        -------

        Notes
        -----
        Only user for postgis vector data
        input parameters: specify the name of the table in the postgis database to be published, specify the store,workspace name, and  the Geoserver user name, password and URL
        """
        try:
            if workspace is None:
                workspace = "default"

            c = pycurl.Curl()
            layer_xml = "<featureType><name>{}</name></featureType>".format(pg_table)
            c.setopt(pycurl.USERPWD, self.username + ":" + self.password)

            # connecting with the specified store in geoserver
            c.setopt(
                c.URL,
                "{}/rest/workspaces/{}/datastores/{}/featuretypes".format(
                    self.service_url, workspace, store_name
                ),
            )
            c.setopt(pycurl.HTTPHEADER, ["Content-type: text/xml"])
            c.setopt(pycurl.POSTFIELDSIZE, len(layer_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(layer_xml).read_cb)
            c.setopt(pycurl.POST, 1)
            c.perform()
            c.close()

        except Exception as e:
            raise e

    def publish_featurestore_sqlview(
        self,
        name: str,
        store_name: str,
        sql: str,
        key_column: str,
        geom_name: str = "geom",
        geom_type: str = "Geometry",
        workspace: Optional[str] = None,
    ):
        """

        Parameters
        ----------
        name : str
        store_name : str
        sql : str
        key_column : str
        geom_name : str
        geom_type : str
        workspace : str, optional

        """
        try:
            if workspace is None:
                workspace = "default"
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
            </featureType>""".format(
                name, sql, key_column, geom_name, geom_type, workspace
            )
            c.setopt(pycurl.USERPWD, self.username + ":" + self.password)
            c.setopt(
                c.URL,
                "{}/rest/workspaces/{}/datastores/{}/featuretypes".format(
                    self.service_url, workspace, store_name
                ),
            )
            c.setopt(pycurl.HTTPHEADER, ["Content-type: text/xml"])
            c.setopt(pycurl.POSTFIELDSIZE, len(layer_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(layer_xml).read_cb)
            c.setopt(pycurl.POST, 1)
            c.perform()
            c.close()
        except Exception as e:
            raise e

    def upload_style(
        self,
        path: str,
        name: Optional[str] = None,
        workspace: Optional[str] = None,
        sld_version: str = "1.0.0",
        overwrite: bool = False,
    ):
        """

        Parameters
        ----------
        path : str
        name : str, optional
        workspace : str, optional
        sld_version : str
        overwrite : bool

        Notes
        -----
        The name of the style file will be, sld_name:workspace
        This function will create the style file in a specified workspace.
        Inputs: path to the sld_file, workspace,
        """
        try:
            if name is None:
                name = os.path.basename(path)
                f = name.split(".")
                if len(f) > 0:
                    name = f[0]

            file_size = os.path.getsize(path)
            url = "{}/rest/workspaces/{}/styles".format(self.service_url, workspace)

            sld_content_type = "application/vnd.ogc.sld+xml"
            if sld_version == "1.1.0" or sld_version == "1.1":
                sld_content_type = "application/vnd.ogc.se+xml"

            if workspace is None:
                # workspace = "default"
                url = "{}/rest/styles".format(self.service_url)

            style_xml = "<style><name>{}</name><filename>{}</filename></style>".format(
                name, name + ".sld"
            )
            # create the xml file for associated style
            c = pycurl.Curl()
            c.setopt(pycurl.USERPWD, self.username + ":" + self.password)
            c.setopt(c.URL, url)
            c.setopt(pycurl.HTTPHEADER, ["Content-type:application/xml"])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(style_xml).read_cb)

            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.perform()

            # upload the style file
            c.setopt(c.URL, "{}/{}".format(url, name))
            c.setopt(pycurl.HTTPHEADER, ["Content-type:{}".format(sld_content_type)])
            c.setopt(pycurl.READFUNCTION, FileReader(open(path, "rb")).read_callback)
            c.setopt(pycurl.INFILESIZE, file_size)
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()
            c.close()

        except Exception as e:
            raise e

    def get_featuretypes(self, workspace: str = None, store_name: str = None):
        """

        Parameters
        ----------
        workspace : str
        store_name : str

        """
        url = "{}/rest/workspaces/{}/datastores/{}/featuretypes.json".format(
            self.service_url, workspace, store_name
        )
        r = requests.get(url, auth=(self.username, self.password))
        r_dict = r.json()
        features = [i["name"] for i in r_dict["featureTypes"]["featureType"]]
        print("Status code: {}, Get feature type".format(r.status_code))

        return features

    def get_feature_attribute(
        self, feature_type_name: str, workspace: str, store_name: str
    ):
        """

        Parameters
        ----------
        feature_type_name : str
        workspace : str
        store_name : str

        """
        url = "{}/rest/workspaces/{}/datastores/{}/featuretypes/{}.json".format(
            self.service_url, workspace, store_name, feature_type_name
        )
        r = requests.get(url, auth=(self.username, self.password))
        r_dict = r.json()
        attribute = [
            i["name"] for i in r_dict["featureType"]["attributes"]["attribute"]
        ]
        print("Status code: {}, Get feature attribute".format(r.status_code))

        return attribute

    def get_featurestore(self, store_name: str, workspace: str):
        """

        Parameters
        ----------
        store_name : str
        workspace : str

        """
        url = "{}/rest/workspaces/{}/datastores/{}".format(
            self.service_url, workspace, store_name
        )
        r = requests.get(url, auth=(self.username, self.password))
        try:
            r_dict = r.json()
            return r_dict["dataStore"]

        except Exception as e:
            return "Error: {}".format(e)

    def create_coveragestyle(
        self,
        raster_path: str,
        style_name: Optional[str] = None,
        workspace: str = None,
        color_ramp: str = "RdYlGn_r",
        cmap_type: str = "ramp",
        number_of_classes: int = 5,
        overwrite: bool = False,
    ):
        """

        Parameters
        ----------
        raster_path : str
        style_name : str, optional
        workspace : str
        color_ramp : str
        cmap_type : str
            # TODO: This should be a set of the available options : {"ramp", "linear", ... }
        number_of_classes : int
        overwrite : bool

        Notes
        -----
        The name of the style file will be, rasterName:workspace
        This function will dynamically create the style file for raster.
        Inputs: name of file, workspace, cmap_type (two options: values, range), ncolors: determins the number of class, min for minimum value of the raster, max for the max value of raster
        """
        try:
            raster = raster_value(raster_path)
            min_value = raster["min"]
            max_value = raster["max"]
            if style_name is None:
                style_name = raster["file_name"]
            coverage_style_xml(
                color_ramp,
                style_name,
                cmap_type,
                min_value,
                max_value,
                number_of_classes,
            )
            style_xml = "<style><name>{}</name><filename>{}</filename></style>".format(
                style_name, style_name + ".sld"
            )

            # create the xml file for associated style
            c = pycurl.Curl()
            c.setopt(pycurl.USERPWD, self.username + ":" + self.password)
            c.setopt(
                c.URL,
                "{}/rest/workspaces/{}/styles".format(self.service_url, workspace),
            )
            c.setopt(pycurl.HTTPHEADER, ["Content-type:text/xml"])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(style_xml).read_cb)
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.perform()

            # upload the style file
            c.setopt(
                c.URL,
                "{}/rest/workspaces/{}/styles/{}".format(
                    self.service_url, workspace, style_name
                ),
            )
            c.setopt(pycurl.HTTPHEADER, ["Content-type:application/vnd.ogc.sld+xml"])
            c.setopt(
                pycurl.READFUNCTION, FileReader(open("style.sld", "rb")).read_callback
            )
            c.setopt(pycurl.INFILESIZE, os.path.getsize("style.sld"))
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()
            c.close()

            # remove temporary style created style file
            os.remove("style.sld")

        except Exception as e:
            return "Error: {}".format(e)

    def create_catagorized_featurestyle(
        self,
        style_name: str,
        column_name: str,
        column_distinct_values,
        workspace: str = None,
        color_ramp: str = "tab20",
        geom_type: str = "polygon",
        outline_color: str = "#3579b1",
        overwrite: bool = False,
    ):
        """Dynamically create categorized style for postgis geometry,

        Parameters
        ----------
        style_name : str
        column_name : str
        column_distinct_values
        workspace : str
        color_ramp : str
        geom_type : str
        outline_color : str
        overwrite : bool

        Notes
        -----

        The data type must be point, line or polygon
        Inputs: column_name (based on which column style should be generated), workspace,
        color_or_ramp (color should be provided in hex code or the color ramp name, geom_type(point, line, polygon), outline_color(hex_color))
        """
        try:
            catagorize_xml(column_name, column_distinct_values, color_ramp, geom_type)

            style_xml = "<style><name>{}</name><filename>{}</filename></style>".format(
                style_name, style_name + ".sld"
            )

            # create the xml file for associated style
            c = pycurl.Curl()
            c.setopt(pycurl.USERPWD, self.username + ":" + self.password)
            c.setopt(
                c.URL,
                "{}/rest/workspaces/{}/styles".format(self.service_url, workspace),
            )
            c.setopt(pycurl.HTTPHEADER, ["Content-type:text/xml"])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(style_xml).read_cb)
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.POST, 1)
            c.perform()

            # upload the style file
            c.setopt(
                c.URL,
                "{}/rest/workspaces/{}/styles/{}".format(
                    self.service_url, workspace, column_name
                ),
            )
            c.setopt(pycurl.HTTPHEADER, ["Content-type:application/vnd.ogc.sld+xml"])
            c.setopt(
                pycurl.READFUNCTION, FileReader(open("style.sld", "rb")).read_callback
            )
            c.setopt(pycurl.INFILESIZE, os.path.getsize("style.sld"))
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()
            c.close()

            # remove temporary style created style file
            os.remove("style.sld")

        except Exception as e:
            raise e

    def create_outline_featurestyle(
        self,
        style_name: str,
        color: str = "#3579b1",
        geom_type: str = "polygon",
        workspace: Optional[str] = None,
        overwrite: bool = False,
    ):
        """Dynamically creates the outline style for postgis geometry

        Parameters
        ----------
        style_name : str
        color : str
        geom_type : str
        workspace : str, optional
        overwrite : bool

        Returns
        -------

        Notes
        -----
        The geometry type must be point, line or polygon
        Inputs: style_name (name of the style file in geoserver), workspace, color (style color)
        """
        try:
            outline_only_xml(color, geom_type)

            style_xml = "<style><name>{}</name><filename>{}</filename></style>".format(
                style_name, style_name + ".sld"
            )

            url = "{}/rest/workspaces/{}/styles".format(self.service_url, workspace)
            if workspace is None:
                url = "{}/rest/styles".format(self.service_url)

            # create the xml file for associated style
            c = pycurl.Curl()
            c.setopt(pycurl.USERPWD, self.username + ":" + self.password)
            c.setopt(c.URL, url)
            c.setopt(pycurl.HTTPHEADER, ["Content-type:text/xml"])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(style_xml).read_cb)
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.perform()

            # upload the style file
            c.setopt(c.URL, "{}/{}".format(url, style_name))
            c.setopt(pycurl.HTTPHEADER, ["Content-type:application/vnd.ogc.sld+xml"])
            c.setopt(
                pycurl.READFUNCTION, FileReader(open("style.sld", "rb")).read_callback
            )
            c.setopt(pycurl.INFILESIZE, os.path.getsize("style.sld"))
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()
            c.close()

            # remove temporary style created style file
            os.remove("style.sld")

        except Exception as e:
            raise e

    def create_classified_featurestyle(
        self,
        style_name: str,
        column_name: str,
        column_distinct_values,
        workspace: Optional[str] = None,
        color_ramp: str = "tab20",
        # geom_type: str = "polygon",
        # outline_color: str = "#3579b1",
        overwrite: bool = False,
    ):
        """Dynamically creates the classified style for postgis geometries.

        Parameters
        ----------
        style_name : str
        column_name : str
        column_distinct_values
        workspace : str, optional
        color_ramp : str
        overwrite : bool

        Notes
        -----
        The data type must be point, line or polygon
        Inputs: column_name (based on which column style should be generated), workspace,
        color_or_ramp (color should be provided in hex code or the color ramp name, geom_type(point, line, polygon), outline_color(hex_color))
        """
        try:
            classified_xml(
                style_name,
                column_name,
                column_distinct_values,
                color_ramp,
                geom_type="polygon",
            )

            style_xml = "<style><name>{}</name><filename>{}</filename></style>".format(
                column_name, column_name + ".sld"
            )

            # create the xml file for associated style
            c = pycurl.Curl()
            c.setopt(pycurl.USERPWD, self.username + ":" + self.password)
            c.setopt(
                c.URL,
                "{}/rest/workspaces/{}/styles".format(self.service_url, workspace),
            )
            c.setopt(pycurl.HTTPHEADER, ["Content-type:text/xml"])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(style_xml).read_cb)
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.POST, 1)
            c.perform()

            # upload the style file
            c.setopt(
                c.URL,
                "{}/rest/workspaces/{}/styles/{}".format(
                    self.service_url, workspace, column_name
                ),
            )
            c.setopt(pycurl.HTTPHEADER, ["Content-type:application/vnd.ogc.sld+xml"])
            c.setopt(
                pycurl.READFUNCTION, FileReader(open("style.sld", "rb")).read_callback
            )
            c.setopt(pycurl.INFILESIZE, os.path.getsize("style.sld"))
            if overwrite:
                c.setopt(pycurl.PUT, 1)
            else:
                c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()
            c.close()

            # remove temporary style created style file
            os.remove("style.sld")

        except Exception as e:
            raise e

    def publish_style(
        self,
        layer_name: str,
        style_name: str,
        workspace: str,
        content_type: str = "text/xml",
    ):
        """Publish a raster file to geoserver.

        Parameters
        ----------
        layer_name : str
        style_name : str
        workspace : str
        content_type : str

        Notes
        -----
        The coverage store will be created automatically as the same name as the raster layer name.
        input parameters: the parameters connecting geoserver (user,password, url and workspace name),
        the path to the file and file_type indicating it is a geotiff, arcgrid or other raster type.

        """

        try:
            c = pycurl.Curl()
            style_xml = (
                "<layer><defaultStyle><name>{}</name></defaultStyle></layer>".format(
                    style_name
                )
            )
            c.setopt(pycurl.USERPWD, self.username + ":" + self.password)
            c.setopt(
                c.URL,
                "{}/rest/layers/{}:{}".format(self.service_url, workspace, layer_name),
            )
            c.setopt(pycurl.HTTPHEADER, ["Content-type: {}".format(content_type)])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(style_xml).read_cb)
            # c.setopt(pycurl.CUSTOMREQUEST, "PUT")
            c.setopt(pycurl.PUT, 1)
            c.perform()
            c.close()
        except Exception as e:
            raise e

    def delete_workspace(self, workspace: str):
        """

        Parameters
        ----------
        workspace : str

        """
        try:
            payload = {"recurse": "true"}
            url = "{}/rest/workspaces/{}".format(self.service_url, workspace)
            r = requests.delete(url, auth=(self.username, self.password), param=payload)

            if r.status_code == 200:
                return "Status code: {}, delete workspace".format(r.status_code)

            else:
                raise Exception("Error: {} {}".format(r.status_code, r.content))

        except Exception as e:
            raise e

    def delete_layer(self, layer_name: str, workspace: Optional[str] = None):
        """

        Parameters
        ----------
        layer_name : str
        workspace : str, optional

        """
        try:
            payload = {"recurse": "true"}
            url = "{}/rest/workspaces/{}/layers/{}".format(
                self.service_url, workspace, layer_name
            )
            if workspace is None:
                url = "{}/rest/layers/{}".format(self.service_url, layer_name)

            r = requests.delete(
                url, auth=(self.username, self.password), params=payload
            )
            if r.status_code == 200:
                return "Status code: {}, delete layer".format(r.status_code)

            else:
                raise Exception("Error: {} {}".format(r.status_code, r.content))

        except Exception as e:
            raise e

    def delete_featurestore(
        self, featurestore_name: str, workspace: Optional[str] = None
    ):
        """

        Parameters
        ----------
        featurestore_name : str
        workspace : str, optional

        """
        try:
            payload = {"recurse": "true"}
            url = "{}/rest/workspaces/{}/datastores/{}".format(
                self.service_url, workspace, featurestore_name
            )
            if workspace is None:
                url = "{}/rest/datastores/{}".format(
                    self.service_url, featurestore_name
                )
            r = requests.delete(
                url, auth=(self.username, self.password), params=payload
            )

            if r.status_code == 200:
                return "Status code: {}, delete featurestore".format(r.status_code)

            else:
                raise Exception("Error: {} {}".format(r.status_code, r.content))

        except Exception as e:
            raise e

    def delete_coveragestore(
        self, coveragestore_name: str, workspace: Optional[str] = None
    ):
        """

        Parameters
        ----------
        coveragestore_name : str
        workspace : str, optional

        """
        try:
            payload = {"recurse": "true"}
            url = "{}/rest/workspaces/{}/coveragestores/{}".format(
                self.service_url, workspace, coveragestore_name
            )

            if workspace is None:
                url = "{}/rest/coveragestores/{}".format(
                    self.service_url, coveragestore_name
                )

            r = requests.delete(
                url, auth=(self.username, self.password), params=payload
            )

            if r.status_code == 200:
                return "Coverage store deleted successfully"

            else:
                raise Exception("Error: {} {}".format(r.status_code, r.content))

        except Exception as e:
            raise e

    def delete_style(self, style_name: str, workspace: Optional[str] = None):
        """

        Parameters
        ----------
        style_name : str
        workspace : str, optional
        """
        try:
            payload = {"recurse": "true"}
            url = "{}/rest/workspaces/{}/styles/{}".format(
                self.service_url, workspace, style_name
            )
            if workspace is None:
                url = "{}/rest/styles/{}".format(self.service_url, style_name)

            r = requests.delete(url, auth=(self.username, self.password), param=payload)

            if r.status_code == 200:
                return "Status code: {}, delete style".format(r.status_code)

            else:
                raise Exception("Error: {} {}".format(r.status_code, r.content))

        except Exception as e:
            raise e
