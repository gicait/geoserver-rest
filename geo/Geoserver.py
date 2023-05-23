# inbuilt libraries
import os
from typing import List, Optional, Set

# third-party libraries
import requests
from xmltodict import parse, unparse

# custom functions
from .Calculation_gdal import raster_value
from .Style import catagorize_xml, classified_xml, coverage_style_xml, outline_only_xml
from .supports import prepare_zip_file


# Custom exceptions.
class GeoserverException(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        super().__init__(f"Status : {self.status} - {self.message}")


# call back class for reading the data
class DataProvider:
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
        service_url: str = "http://localhost:8080/geoserver",  # default deployment url during installation
        username: str = "admin",  # default username during geoserver installation
        password: str = "geoserver",  # default password during geoserver installation
    ):
        self.service_url = service_url
        self.username = username
        self.password = password

        # private request method to reduce repetition of putting auth(username,password) in all requests call. DRY principle

    def _requests(self, method: str, url: str, **kwargs) -> requests.Response:
        if method == "post":
            return requests.post(url, auth=(self.username, self.password), **kwargs)
        elif method == "get":
            return requests.get(url, auth=(self.username, self.password), **kwargs)
        elif method == "put":
            return requests.put(url, auth=(self.username, self.password), **kwargs)
        elif method == "delete":
            return requests.delete(url, auth=(self.username, self.password), **kwargs)

    # _______________________________________________________________________________________________
    #
    #       GEOSERVER AND SERVER SPECIFIC METHODS
    # _______________________________________________________________________________________________
    #

    def get_manifest(self):
        """
        Returns the manifest of the geoserver. The manifest is a JSON of all the loaded JARs on the GeoServer server.

        """
        url = "{}/rest/about/manifest.json".format(self.service_url)
        r = requests.get(url, auth=(self.username, self.password))
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_version(self):
        """
        Returns the version of the geoserver as JSON. It contains only the details of the high level components: GeoServer, GeoTools, and GeoWebCache
        """
        url = "{}/rest/about/version.json".format(self.service_url)
        r = self._requests("get", url)
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_status(self):
        """
        Returns the status of the geoserver. It shows the status details of all installed and configured modules.
        """
        url = "{}/rest/about/status.json".format(self.service_url)
        r = requests.get(url, auth=(self.username, self.password))
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_system_status(self):
        """
        It returns the system status of the geoserver. It returns a list of system-level information. Major operating systems (Linux, Windows and MacOX) are supported out of the box.
        """
        url = "{}/rest/about/system-status.json".format(self.service_url)
        r = requests.get(url, auth=(self.username, self.password))
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def reload(self):
        """
        Reloads the GeoServer catalog and configuration from disk.

        This operation is used in cases where an external tool has modified the on-disk configuration.
        This operation will also force GeoServer to drop any internal caches and reconnect to all data stores.
        curl -X POST http://localhost:8080/geoserver/rest/reload -H  "accept: application/json" -H  "content-type: application/json"
        """
        url = "{}/rest/reload".format(self.service_url)
        r = requests.post(url, auth=(self.username, self.password))
        if r.status_code == 200:
            return "Status code: {}".format(r.status_code)
        else:
            raise GeoserverException(r.status_code, r.content)

    def reset(self):
        """
        Resets all store, raster, and schema caches. This operation is used to force GeoServer to drop all caches and
        store connections and reconnect to each of them the next time they are needed by a request. This is useful in
        case the stores themselves cache some information about the data structures they manage that may have changed
        in the meantime.
        curl -X POST http://localhost:8080/geoserver/rest/reset -H  "accept: application/json" -H  "content-type: application/json"
        """
        url = "{}/rest/reset".format(self.service_url)
        r = requests.post(url, auth=(self.username, self.password))
        if r.status_code == 200:
            return "Status code: {}".format(r.status_code)
        else:
            raise GeoserverException(r.status_code, r.content)

    # _______________________________________________________________________________________________
    #
    #      WORKSPACES
    # _______________________________________________________________________________________________
    #

    def get_default_workspace(self):
        """
        Returns the default workspace.
        """
        url = "{}/rest/workspaces/default".format(self.service_url)
        r = requests.get(url, auth=(self.username, self.password))
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_workspace(self, workspace):
        """
        get name  workspace if exist
        Example: curl -v -u admin:admin -XGET -H "Accept: text/xml"  http://localhost:8080/geoserver/rest/workspaces/acme.xml
        """
        payload = {"recurse": "true"}
        url = "{}/rest/workspaces/{}.json".format(self.service_url, workspace)
        r = requests.get(url, auth=(self.username, self.password), params=payload)
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_workspaces(self):
        """
        Returns all the workspaces.
        """
        url = "{}/rest/workspaces".format(self.service_url)
        r = requests.get(url, auth=(self.username, self.password))
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def set_default_workspace(self, workspace: str):
        """
        Set the default workspace.
        """
        url = "{}/rest/workspaces/default".format(self.service_url)
        data = "<workspace><name>{}</name></workspace>".format(workspace)
        print(url, data)
        r = self._requests(
            "put",
            url,
            data=data,
            headers={"content-type": "text/xml"},
        )

        if r.status_code == 200:
            return "Status code: {}, default workspace {} set!".format(
                r.status_code, workspace
            )
        else:
            raise GeoserverException(r.status_code, r.content)

    def create_workspace(self, workspace: str):
        """
        Create a new workspace in geoserver.

        The geoserver workspace url will be same as the name of the workspace.
        """
        url = "{}/rest/workspaces".format(self.service_url)
        data = "<workspace><name>{}</name></workspace>".format(workspace)
        headers = {"content-type": "text/xml"}
        r = self._requests("post", url, data=data, headers=headers)

        if r.status_code == 201:
            return "{} Workspace {} created!".format(r.status_code, workspace)
        else:
            raise GeoserverException(r.status_code, r.content)

    def delete_workspace(self, workspace: str):
        """

        Parameters
        ----------
        workspace : str

        """
        payload = {"recurse": "true"}
        url = "{}/rest/workspaces/{}".format(self.service_url, workspace)
        r = requests.delete(url, auth=(self.username, self.password), params=payload)

        if r.status_code == 200:
            return "Status code: {}, delete workspace".format(r.status_code)

        else:
            raise GeoserverException(r.status_code, r.content)

    # _______________________________________________________________________________________________
    #
    #       DATASTORES
    # _______________________________________________________________________________________________
    #

    def get_datastore(self, store_name: str, workspace: Optional[str] = None):
        """
        Return the data store in a given workspace.

        If workspace is not provided, it will take the default workspace
        curl -X GET http://localhost:8080/geoserver/rest/workspaces/demo/datastores -H  "accept: application/xml" -H  "content-type: application/json"
        """
        if workspace is None:
            workspace = "default"

        url = "{}/rest/workspaces/{}/datastores/{}".format(
            self.service_url, workspace, store_name
        )

        r = self._requests("get", url)

        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_datastores(self, workspace: Optional[str] = None):
        """
        List all data stores in a workspace.

        If workspace is not provided, it will listout all the datastores inside default workspace
        curl -X GET http://localhost:8080/geoserver/rest/workspaces/demo/datastores -H  "accept: application/xml" -H  "content-type: application/json"
        """
        if workspace is None:
            workspace = "default"

        url = "{}/rest/workspaces/{}/datastores.json".format(
            self.service_url, workspace
        )
        r = requests.get(url, auth=(self.username, self.password))
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    # _______________________________________________________________________________________________
    #
    #       COVERAGE STORES
    # _______________________________________________________________________________________________
    #

    def get_coveragestore(
        self, coveragestore_name: str, workspace: Optional[str] = None
    ):
        """
        Returns the store name if it exists.
        """
        payload = {"recurse": "true"}
        if workspace is None:
            workspace = "default"
        url = "{}/rest/workspaces/{}/coveragestores/{}.json".format(
            self.service_url, workspace, coveragestore_name
        )
        r = self._requests(method="get", url=url, params=payload)
        # print("Status code: {}, Get coverage store".format(r.status_code))

        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_coveragestores(self, workspace: str = None):
        """
        Returns all the coveragestores inside a specific workspace.
        """
        if workspace is None:
            workspace = "default"

        url = "{}/rest/workspaces/{}/coveragestores".format(self.service_url, workspace)
        r = requests.get(url, auth=(self.username, self.password))
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def create_coveragestore(
        self,
        path,
        workspace: Optional[str] = None,
        layer_name: Optional[str] = None,
        file_type: str = "GeoTIFF",
        content_type: str = "image/tiff",
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
        if path is None:
            raise Exception("You must provide the full path to the raster")

        if workspace is None:
            workspace = "default"

        if layer_name is None:
            layer_name = os.path.basename(path)
            f = layer_name.split(".")
            if len(f) > 0:
                layer_name = f[0]

        file_type = file_type.lower()

        url = "{0}/rest/workspaces/{1}/coveragestores/{2}/file.{3}?coverageName={2}".format(
            self.service_url, workspace, layer_name, file_type
        )

        headers = {"content-type": content_type, "Accept": "application/json"}

        r = None
        with open(path, "rb") as f:
            r = self._requests(method="put", url=url, data=f, headers=headers)

            if r.status_code == 201:
                return r.json()
            else:
                raise GeoserverException(r.status_code, r.content)

    def publish_time_dimension_to_coveragestore(
        self,
        store_name: Optional[str] = None,
        workspace: Optional[str] = None,
        presentation: Optional[str] = "LIST",
        units: Optional[str] = "ISO8601",
        default_value: Optional[str] = "MINIMUM",
        content_type: str = "application/xml; charset=UTF-8",
    ):
        """
        Create time dimension in coverage store to publish time series in geoserver.

        Parameters
        ----------
        store_name : str, optional
        workspace : str, optional
        presentation : str, optional
        units : str, optional
        default_value : str, optional
        content_type : str

        Notes
        -----
        More about time support in geoserver WMS you can read here:
        https://docs.geoserver.org/master/en/user/services/wms/time.html
        """

        url = "{0}/rest/workspaces/{1}/coveragestores/{2}/coverages/{2}".format(
            self.service_url, workspace, store_name
        )

        headers = {"content-type": content_type}

        time_dimension_data = (
            "<coverage>"
            "<enabled>true</enabled>"
            "<metadata>"
            "<entry key='time'>"
            "<dimensionInfo>"
            "<enabled>true</enabled>"
            "<presentation>{}</presentation>"
            "<units>{}</units>"
            "<defaultValue>"
            "<strategy>{}</strategy>"
            "</defaultValue>"
            "</dimensionInfo>"
            "</entry>"
            "</metadata>"
            "</coverage>".format(presentation, units, default_value)
        )

        r = self._requests(
            method="put", url=url, data=time_dimension_data, headers=headers
        )
        if r.status_code in [200, 201]:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    # _______________________________________________________________________________________________
    #
    #       LAYERS
    # _______________________________________________________________________________________________
    #

    def get_layer(self, layer_name: str, workspace: Optional[str] = None):
        """
        Returns the layer by layer name.
        """
        url = "{}/rest/layers/{}".format(self.service_url, layer_name)
        if workspace is not None:
            url = "{}/rest/workspaces/{}/layers/{}".format(
                self.service_url, workspace, layer_name
            )

        r = self._requests("get", url)
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_layers(self, workspace: Optional[str] = None):
        """
        Get all the layers from geoserver
        If workspace is None, it will listout all the layers from geoserver
        """
        url = "{}/rest/layers".format(self.service_url)

        if workspace is not None:
            url = "{}/rest/workspaces/{}/layers".format(self.service_url, workspace)
        r = requests.get(url, auth=(self.username, self.password))
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def delete_layer(self, layer_name: str, workspace: Optional[str] = None):
        """

        Parameters
        ----------
        layer_name : str
        workspace : str, optional

        """
        payload = {"recurse": "true"}
        url = "{}/rest/workspaces/{}/layers/{}".format(
            self.service_url, workspace, layer_name
        )
        if workspace is None:
            url = "{}/rest/layers/{}".format(self.service_url, layer_name)

        r = self._requests(method="delete", url=url, params=payload)
        if r.status_code == 200:
            return "Status code: {}, delete layer".format(r.status_code)
        else:
            raise GeoserverException(r.status_code, r.content)

    # _______________________________________________________________________________________________
    #
    #       LAYER GROUPS
    # _______________________________________________________________________________________________
    #

    def get_layergroups(self, workspace: Optional[str] = None):
        """
        Returns all the layer groups from geoserver.

        Notes
        -----
        If workspace is None, it will list all the layer groups from geoserver.
        """
        url = "{}/rest/layergroups".format(self.service_url)

        if workspace is not None:
            url = "{}/rest/workspaces/{}/layergroups".format(
                self.service_url, workspace
            )
        r = requests.get(url, auth=(self.username, self.password))
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_layergroup(self, layer_name: str, workspace: Optional[str] = None):
        """
        Returns the layer group by layer group name.
        """
        url = "{}/rest/layergroups/{}".format(self.service_url, layer_name)
        if workspace is not None:
            url = "{}/rest/workspaces/{}/layergroups/{}".format(
                self.service_url, workspace, layer_name
            )
        r = self._requests("get", url)
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def create_layergroup(
        self,
        name: str = "geoserver-rest-layergroup",
        mode: str = "single",
        title: str = "geoserver-rest layer group",
        abstract_text: str = "A new layergroup created with geoserver-rest python package",
        layers: List[str] = [],
        workspace: Optional[str] = None,
        formats: str = "html",
        metadata: List[dict] = [],
        keywords: List[str] = [],
    ) -> str:
        """
        Creates the Layergroup.

        Parameters
        ----------
        name : str
        mode : str
        title : str
        abstract_text : str
        layers : list
        workspace : str, optional
        formats : str, optional
        metadata : list, optional
        keywords : list, optional

        Notes
        -----
        title is a human readable text for the layergroup
        abstract_text is a long text, like a brief info about the layergroup
        workspace is Optional(Global Layergroups don't need workspace).A layergroup can exist without a workspace.
        """
        assert isinstance(name, str), "Name must be of type String:''"
        assert isinstance(mode, str), "Mode must be of type String:''"
        assert isinstance(title, str), "Title must be of type String:''"
        assert isinstance(abstract_text, str), "Abstract text must be of type String:''"
        assert isinstance(formats, str), "Format must be of type String:''"
        assert isinstance(
            metadata, list
        ), "Metadata must be of type List of dict:[{'about':'geoserver rest data metadata','content_url':'lint to content url'}]"
        assert isinstance(
            keywords, list
        ), "Keywords must be of type List:['keyword1','keyword2'...]"
        assert isinstance(
            layers, list
        ), "Layers must be of type List:['layer1','layer2'...]"

        if workspace:
            assert isinstance(workspace, str), "Workspace must be of type String:''"
            # check if the workspace is valid in Geoserver
            if self.get_workspace(workspace) is None:
                raise Exception("Workspace is not valid in Geoserver Instance")

        supported_modes: Set = {
            "single",
            "opaque container",
            "named tree",
            "container tree",
            "earth observation tree",
        }
        supported_formats: Set = {"html", "json", "xml"}

        if mode.lower() != "single" and mode.lower() not in supported_modes:
            raise Exception(
                f"Mode not supported. Acceptable modes are : {supported_modes}"
            )

        if formats.lower() != "html" and formats.lower() not in supported_formats:
            raise Exception(
                f"Format not supported. Acceptable formats are : {supported_formats}"
            )

        # check if it already exist in Geoserver
        try:
            existing_layergroup = self.get_layergroup(name, workspace=workspace)
        except GeoserverException:
            existing_layergroup = None

        if existing_layergroup is not None:
            raise Exception(f"Layergroup: {name} already exist in Geoserver instance")

        if len(layers) == 0:
            raise Exception("No layer provided!")
        else:
            for layer in layers:
                # check if it is valid in geoserver

                if (
                    self.get_layer(
                        layer_name=layer,
                        workspace=workspace if workspace is not None else None,
                    )
                    is not None
                ):
                    ...
                else:
                    raise Exception(
                        f"Layer: {layer} is not a valid layer in the Geoserver instance"
                    )

        skeleton = ""

        if workspace:
            skeleton += f"<workspace><name>{workspace}</name></workspace>"
        # metadata structure = [{about:"",content_url:""},{...}]
        metadata_xml_list = []

        if len(metadata) >= 1:
            for meta in metadata:
                metadata_about = meta.get("about")
                metadata_content_url = meta.get("content_url")
                metadata_xml_list.append(
                    f"""
                            <metadataLink>
                                <type>text/plain</type>
                                <about>{metadata_about}</about>
                                <metadataType>ISO19115:2003</metadataType>
                                <content>{metadata_content_url}</content>
                            </metadataLink>
                            """
                )

            metadata_xml = f"<metadataLinks>{''.join(['{}'] * len(metadata_xml_list)).format(*metadata_xml_list)}</metadataLinks>"
            skeleton += metadata_xml
        layers_xml_list: List[str] = []

        for layer in layers:
            layers_xml_list.append(
                f"""<published type="layer">
                            <name>{layer}</name>
                            <link>{self.service_url}/layers/{layer}.xml</link>
                        </published>
                    """
            )

        layers_xml: str = f"<publishables>{''.join(['{}'] * len(layers)).format(*layers_xml_list)}</publishables>"
        skeleton += layers_xml

        if len(keywords) >= 1:
            keyword_xml_list: List[str] = [
                f"<keyword>{keyword}</keyword>" for keyword in keywords
            ]
            keywords_xml: str = f"<keywords>{''.join(['{}'] * len(keywords)).format(*keyword_xml_list)}</keywords>"
            skeleton += keywords_xml

        data = f"""
                    <layerGroup>
                        <name>{name}</name>
                        <mode>{mode}</mode>
                        <title>{title}</title>
                        <abstractTxt>{abstract_text}</abstractTxt>
                        {skeleton}
                    </layerGroup>
                """

        url = f"{self.service_url}/rest/layergroups/"

        r = self._requests(
            method="post", url=url, data=data, headers={"content-type": "text/xml"}
        )
        if r.status_code == 201:
            layergroup_url = f"{self.service_url}/rest/layergroups/{name}.{formats}"
            return f"layergroup created successfully! Layergroup link: {layergroup_url}"
        else:
            raise GeoserverException(r.status_code, r.content)

    def update_layergroup(
        self,
        layergroup_name,
        title: Optional[str] = None,
        abstract_text: Optional[str] = None,
        formats: str = "html",
        metadata: List[dict] = [],
        keywords: List[str] = [],
    ) -> str:
        """
        Updates a Layergroup.

        Parameters
        ----------
        layergroup_name: str, required
        mode : str, optional
        title : str, optional
        abstract_text : str, optional
        formats : str, optional
        metadata : list, optional
        keywords : list, optional

        """
        # check if layergroup is valid in Geoserver

        if self.get_layergroup(layer_name=layergroup_name) is None:
            raise Exception(
                f"Layer group: {layergroup_name} is not a valid layer group in the Geoserver instance"
            )
        if title is not None:
            assert isinstance(title, str), "Title must be of type String:''"
        if abstract_text is not None:
            assert isinstance(
                abstract_text, str
            ), "Abstract text must be of type String:''"
        assert isinstance(formats, str), "Format must be of type String:''"
        assert isinstance(
            metadata, list
        ), "Metadata must be of type List of dict:[{'about':'geoserver rest data metadata','content_url':'lint to content url'}]"
        assert isinstance(
            keywords, list
        ), "Keywords must be of type List:['keyword1','keyword2'...]"

        supported_formats: Set = {"html", "json", "xml"}

        if formats.lower() != "html" and formats.lower() not in supported_formats:
            raise Exception(
                f"Format not supported. Acceptable formats are : {supported_formats}"
            )

        skeleton = ""

        if title:
            skeleton += f"<title>{title}</title>"
        if abstract_text:
            skeleton += f"<abstractTxt>{abstract_text}</abstractTxt>"

        metadata_xml_list = []

        if len(metadata) >= 1:
            for meta in metadata:
                metadata_about = meta.get("about")
                metadata_content_url = meta.get("content_url")
                metadata_xml_list.append(
                    f"""
                            <metadataLink>
                                <type>text/plain</type>
                                <about>{metadata_about}</about>
                                <metadataType>ISO19115:2003</metadataType>
                                <content>{metadata_content_url}</content>
                            </metadataLink>
                            """
                )

            metadata_xml = f"<metadataLinks>{''.join(['{}'] * len(metadata_xml_list)).format(*metadata_xml_list)}</metadataLinks>"
            skeleton += metadata_xml

        if len(keywords) >= 1:
            keyword_xml_list: List[str] = [
                f"<keyword>{keyword}</keyword>" for keyword in keywords
            ]
            keywords_xml: str = f"<keywords>{''.join(['{}'] * len(keywords)).format(*keyword_xml_list)}</keywords>"
            skeleton += keywords_xml

        data = f"""
                    <layerGroup>
                        {skeleton}
                    </layerGroup>
                """

        url = f"{self.service_url}/rest/layergroups/{layergroup_name}"

        r = self._requests(
            method="put",
            url=url,
            data=data,
            headers={"content-type": "text/xml", "accept": "application/xml"},
        )
        if r.status_code == 200:
            layergroup_url = (
                f"{self.service_url}/rest/layergroups/{layergroup_name}.{formats}"
            )
            return f"layergroup updated successfully! Layergroup link: {layergroup_url}"
        else:
            raise GeoserverException(r.status_code, r.content)

    def delete_layergroup(
        self, layergroup_name: str, workspace: Optional[str] = None
    ) -> str:
        """
        Delete a layer group from the geoserver and raise an exception
        in case the layer group does not exist, or the geoserver is unavailable.

        Parameters
        ----------
        layergroup_name: str, required The name of the layer group to be deleted
        workspace: str, optional The workspace the layergroup is located in
        """
        # raises an exception in case the layer group doesn't exist
        self.get_layergroup(layer_name=layergroup_name, workspace=workspace)

        if workspace is None:
            url = f"{self.service_url}/rest/layergroups/{layergroup_name}"
        else:
            url = f"{self.service_url}/rest/workspaces/{workspace}/layergroups/{layergroup_name}"

        r = self._requests(url=url, method="delete")
        if r.status_code == 200:
            return "Layer group deleted successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

    def add_layer_to_layergroup(
        self,
        layer_name: str,
        layer_workspace: str,
        layergroup_name: str,
        layergroup_workspace: str = None,
    ) -> None:
        """
        Add the specified layer to an existing layer group and raise an exception if
        either the layer or layergroup doesn't exist, or the geoserver is unavailable.

        Parameters
        ----------
        layer_name: str, required The name of the layer
        layer_workspace: str, required The workspace the layer is located in
        layergroup_workspace: str, optional The workspace the layergroup is located in
        layergroup_name: str, required The name of the layer group
        layergroup_workspace: str, optional The workspace the layergroup is located in
        """

        layergroup_info = self.get_layergroup(
            layer_name=layergroup_name, workspace=layergroup_workspace
        )
        layer_info = self.get_layer(layer_name=layer_name, workspace=layer_workspace)

        # build list of existing publishables & styles
        publishables = layergroup_info["layerGroup"]["publishables"]["published"]
        if not isinstance(publishables, list):  # only 1 layer up to now
            publishables = [publishables]

        styles = layergroup_info["layerGroup"]["styles"]["style"]
        if not isinstance(styles, list):  # only 1 layer up to now
            styles = [styles]

        # add publishable & style for the new layer
        new_pub = {
            "name": f"{layer_workspace}:{layer_name}",
            "href": f"{self.service_url}/rest/workspaces/{layer_workspace}/layers/{layer_name}.json",
        }
        publishables.append(new_pub)

        new_style = layer_info["layer"]["defaultStyle"]
        styles.append(new_style)

        data = self._layergroup_definition_from_layers_and_styles(
            publishables=publishables, styles=styles
        )

        if layergroup_workspace is None:
            url = f"{self.service_url}/rest/layergroups/{layergroup_name}"
        else:
            url = f"{self.service_url}/rest/workspaces/{layergroup_workspace}/layergroups/{layergroup_name}"

        r = self._requests(
            method="put",
            url=url,
            data=data,
            headers={"content-type": "text/xml", "accept": "application/xml"},
        )
        if r.status_code == 200:
            return
        else:
            raise GeoserverException(r.status_code, r.content)

    def remove_layer_from_layergroup(
        self,
        layer_name: str,
        layer_workspace: str,
        layergroup_name: str,
        layergroup_workspace: str = None,
    ) -> None:
        """
        Add remove the specified layer from an existing layer group and raise an exception if
        either the layer or layergroup doesn't exist, or the geoserver is unavailable.

        Parameters
        ----------
        layer_name: str, required The name of the layer
        layer_workspace: str, required The workspace the layer is located in
        layergroup_workspace: str, optional The workspace the layergroup is located in
        layergroup_name: str, required The name of the layer group
        layergroup_workspace: str, optional The workspace the layergroup is located in
        """

        layergroup_info = self.get_layergroup(
            layer_name=layergroup_name, workspace=layergroup_workspace
        )

        # build list of existing publishables & styles
        publishables = layergroup_info["layerGroup"]["publishables"]["published"]
        if not isinstance(publishables, list):  # only 1 layer up to now
            publishables = [publishables]

        styles = layergroup_info["layerGroup"]["styles"]["style"]
        if not isinstance(styles, list):  # only 1 layer up to now
            styles = [styles]

        layer_to_remove = f"{layer_workspace}:{layer_name}"

        revised_set_of_publishables_and_styles = [
            (pub, style)
            for (pub, style) in zip(
                layergroup_info["layerGroup"]["publishables"]["published"],
                layergroup_info["layerGroup"]["styles"]["style"],
            )
            if pub["name"] != layer_to_remove
        ]

        revised_set_of_publishables = list(
            map(list, zip(*revised_set_of_publishables_and_styles))
        )[0]
        revised_set_of_styles = list(
            map(list, zip(*revised_set_of_publishables_and_styles))
        )[1]

        xml_payload = self._layergroup_definition_from_layers_and_styles(
            publishables=revised_set_of_publishables, styles=revised_set_of_styles
        )

        if layergroup_workspace is None:
            url = f"{self.service_url}/rest/layergroups/{layergroup_name}"
        else:
            url = f"{self.service_url}/rest/workspaces/{layergroup_workspace}/layergroups/{layergroup_name}"

        r = self._requests(
            method="put",
            url=url,
            data=xml_payload,
            headers={"content-type": "text/xml", "accept": "application/xml"},
        )
        if r.status_code == 200:
            return
        else:
            raise GeoserverException(r.status_code, r.content)

    def _layergroup_definition_from_layers_and_styles(
        self, publishables: list, styles: list
    ) -> str:
        """
        Helper function for add_layer_to_layergroup and remove_layer_from_layergroup

        Parameters
        ----------
        layer_name: str, required The name of the layer
        layer_workspace: str, required The workspace the layer is located in

        Returns
        -------
        Formatted xml request body for PUT layergroup
        """

        # the get_layergroup method may return an empty string for style;
        # so we get the default styles for each layer with no style information in the layergroup
        if len(styles) == 1:
            index = [0]
        else:
            index = range(len(styles))

        for ix, this_style, this_layer in zip(index, styles, publishables):
            if this_style == "":
                this_layer_info = self.get_layer(
                    layer_name=this_layer["name"].split(":")[1],
                    workspace=this_layer["name"].split(":")[0],
                )
                styles[ix] = {
                    "name": this_layer_info["layer"]["defaultStyle"]["name"],
                    "href": this_layer_info["layer"]["defaultStyle"]["href"],
                }

        # build xml structure
        layer_skeleton = ""
        style_skeleton = ""

        for publishable in publishables:
            layer_str = f"""
                <published type="layer">
                    <name>{publishable['name']}</name>
                    <link>{publishable['href']}</link>
                </published>
            """
            layer_skeleton += layer_str

        for style in styles:
            style_str = f"""
                <style>
                    <name>{style['name']}</name>
                    <link>{style['href']}</link>
                </style>
            """
            style_skeleton += style_str

        data = f"""
                <layerGroup>
                    <publishables>
                        {layer_skeleton}
                    </publishables>
                    <styles>
                        {style_skeleton}
                    </styles>
                </layerGroup>
                """

        return data

    # _______________________________________________________________________________________________
    #
    #      STYLES
    # _______________________________________________________________________________________________
    #

    def get_style(self, style_name, workspace: Optional[str] = None):
        """
        Returns the style by style name.
        """
        url = "{}/rest/styles/{}.json".format(self.service_url, style_name)
        if workspace is not None:
            url = "{}/rest/workspaces/{}/styles/{}.json".format(
                self.service_url, workspace, style_name
            )

        r = self._requests("get", url)

        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_styles(self, workspace: Optional[str] = None):
        """
        Returns all loaded styles from geoserver.
        """
        url = "{}/rest/styles.json".format(self.service_url)

        if workspace is not None:
            url = "{}/rest/workspaces/{}/styles.json".format(
                self.service_url, workspace
            )
        r = requests.get(url, auth=(self.username, self.password))
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def upload_style(
        self,
        path: str,
        name: Optional[str] = None,
        workspace: Optional[str] = None,
        sld_version: str = "1.0.0",
    ):
        """

        Parameters
        ----------
        path : str
        name : str, optional
        workspace : str, optional
        sld_version : str, optional

        Notes
        -----
        The name of the style file will be, sld_name:workspace
        This function will create the style file in a specified workspace.
        Inputs: path to the sld_file, workspace,
        """
        if name is None:
            name = os.path.basename(path)
            f = name.split(".")
            if len(f) > 0:
                name = f[0]

        headers = {"content-type": "text/xml"}

        url = "{}/rest/workspaces/{}/styles".format(self.service_url, workspace)

        sld_content_type = "application/vnd.ogc.sld+xml"
        if sld_version == "1.1.0" or sld_version == "1.1":
            sld_content_type = "application/vnd.ogc.se+xml"

        header_sld = {"content-type": sld_content_type}

        if workspace is None:
            # workspace = "default"
            url = "{}/rest/styles".format(self.service_url)

        style_xml = "<style><name>{}</name><filename>{}</filename></style>".format(
            name, name + ".sld"
        )

        r = self._requests(method="post", url=url, data=style_xml, headers=headers)
        if r.status_code == 201:
            with open(path, "rb") as f:
                r_sld = requests.put(
                    url + "/" + name,
                    data=f.read(),
                    auth=(self.username, self.password),
                    headers=header_sld,
                )
            if r_sld.status_code == 200:
                return r_sld.status_code
            else:
                raise GeoserverException(r_sld.status_code, r_sld.content)

        else:
            raise GeoserverException(r.status_code, r.content)

    def create_coveragestyle(
        self,
        raster_path: str,
        style_name: Optional[str] = None,
        workspace: str = None,
        color_ramp: str = "RdYlGn_r",
        cmap_type: str = "ramp",
        number_of_classes: int = 5,
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
        Inputs: name of file, workspace, cmap_type (two options: values, range), ncolors: determines the number of class, min for minimum value of the raster, max for the max value of raster
        """
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

        if style_name is None:
            style_name = os.path.basename(raster_path)
            f = style_name.split(".")
            if len(f) > 0:
                style_name = f[0]

        headers = {"content-type": "text/xml"}
        url = "{}/rest/workspaces/{}/styles".format(self.service_url, workspace)
        sld_content_type = "application/vnd.ogc.sld+xml"
        header_sld = {"content-type": sld_content_type}

        if workspace is None:
            url = "{}/rest/styles".format(self.service_url)

        r = self._requests(
            "post",
            url,
            data=style_xml,
            headers=headers,
        )
        if r.status_code == 201:
            with open("style.sld", "rb") as f:
                r_sld = requests.put(
                    url + "/" + style_name,
                    data=f.read(),
                    auth=(self.username, self.password),
                    headers=header_sld,
                )
            os.remove("style.sld")
            if r_sld.status_code == 200:
                return r_sld.status_code
            else:
                raise GeoserverException(r_sld.status_code, r_sld.content)

        else:
            raise GeoserverException(r.status_code, r.content)

    def create_catagorized_featurestyle(
        self,
        style_name: str,
        column_name: str,
        column_distinct_values,
        workspace: str = None,
        color_ramp: str = "tab20",
        geom_type: str = "polygon",
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
        catagorize_xml(column_name, column_distinct_values, color_ramp, geom_type)

        style_xml = "<style><name>{}</name><filename>{}</filename></style>".format(
            style_name, style_name + ".sld"
        )

        headers = {"content-type": "text/xml"}
        url = "{}/rest/workspaces/{}/styles".format(self.service_url, workspace)
        sld_content_type = "application/vnd.ogc.sld+xml"
        header_sld = {"content-type": sld_content_type}

        if workspace is None:
            url = "{}/rest/styles".format(self.service_url)

        r = self._requests(
            "post",
            url,
            data=style_xml,
            headers=headers,
        )
        if r.status_code == 201:
            with open("style.sld", "rb") as f:
                r_sld = self._requests(
                    "put",
                    url + "/" + style_name,
                    data=f.read(),
                    headers=header_sld,
                )
            os.remove("style.sld")
            if r_sld.status_code == 200:
                return r_sld.status_code
            else:
                raise GeoserverException(r_sld.status_code, r_sld.content)

        else:
            raise GeoserverException(r.status_code, r.content)

    def create_outline_featurestyle(
        self,
        style_name: str,
        color: str = "#3579b1",
        geom_type: str = "polygon",
        workspace: Optional[str] = None,
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
        outline_only_xml(color, geom_type)

        style_xml = "<style><name>{}</name><filename>{}</filename></style>".format(
            style_name, style_name + ".sld"
        )

        headers = {"content-type": "text/xml"}
        url = "{}/rest/workspaces/{}/styles".format(self.service_url, workspace)
        sld_content_type = "application/vnd.ogc.sld+xml"
        header_sld = {"content-type": sld_content_type}

        if workspace is None:
            url = "{}/rest/styles".format(self.service_url)

        r = self._requests(
            "post",
            url,
            data=style_xml,
            headers=headers,
        )
        if r.status_code == 201:
            with open("style.sld", "rb") as f:
                r_sld = self._requests(
                    "put",
                    url + "/" + style_name,
                    data=f.read(),
                    headers=header_sld,
                )
            os.remove("style.sld")
            if r_sld.status_code == 200:
                return r_sld.status_code
            else:
                raise GeoserverException(r_sld.status_code, r_sld.content)

        else:
            raise GeoserverException(r.status_code, r.content)

    def create_classified_featurestyle(
        self,
        style_name: str,
        column_name: str,
        column_distinct_values,
        workspace: Optional[str] = None,
        color_ramp: str = "tab20",
        geom_type: str = "polygon",
        # outline_color: str = "#3579b1",
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
        classified_xml(
            style_name,
            column_name,
            column_distinct_values,
            color_ramp,
            geom_type,
        )

        style_xml = "<style><name>{}</name><filename>{}</filename></style>".format(
            column_name, column_name + ".sld"
        )

        headers = {"content-type": "text/xml"}
        url = "{}/rest/workspaces/{}/styles".format(self.service_url, workspace)
        sld_content_type = "application/vnd.ogc.sld+xml"
        header_sld = {"content-type": sld_content_type}

        if workspace is None:
            url = "{}/rest/styles".format(self.service_url)

        r = self._requests(
            "post",
            url,
            data=style_xml,
            headers=headers,
        )
        if r.status_code == 201:
            with open("style.sld", "rb") as f:
                r_sld = self._requests(
                    "put",
                    url + "/" + style_name,
                    data=f.read(),
                    headers=header_sld,
                )
            os.remove("style.sld")
            if r_sld.status_code == 200:
                return r_sld.status_code
            else:
                raise GeoserverException(r_sld.status_code, r_sld.content)

        else:
            raise GeoserverException(r.status_code, r.content)

    def publish_style(
        self,
        layer_name: str,
        style_name: str,
        workspace: str,
    ):
        """Publish a raster file to geoserver.

        Parameters
        ----------
        layer_name : str
        style_name : str
        workspace : str

        Notes
        -----
        The coverage store will be created automatically as the same name as the raster layer name.
        input parameters: the parameters connecting geoserver (user,password, url and workspace name),
        the path to the file and file_type indicating it is a geotiff, arcgrid or other raster type.

        """
        headers = {"content-type": "text/xml"}
        url = "{}/rest/layers/{}:{}".format(self.service_url, workspace, layer_name)
        style_xml = (
            "<layer><defaultStyle><name>{}</name></defaultStyle></layer>".format(
                style_name
            )
        )

        r = self._requests(
            "put",
            url,
            data=style_xml,
            headers=headers,
        )
        if r.status_code == 200:
            return r.status_code
        else:
            raise GeoserverException(r.status_code, r.content)

    def delete_style(self, style_name: str, workspace: Optional[str] = None):
        """

        Parameters
        ----------
        style_name : str
        workspace : str, optional
        """
        payload = {"recurse": "true"}
        url = "{}/rest/workspaces/{}/styles/{}".format(
            self.service_url, workspace, style_name
        )
        if workspace is None:
            url = "{}/rest/styles/{}".format(self.service_url, style_name)

        r = self._requests("delete", url, params=payload)

        if r.status_code == 200:
            return "Status code: {}, delete style".format(r.status_code)
        else:
            raise GeoserverException(r.status_code, r.content)

    # _______________________________________________________________________________________________
    #
    #      FEATURES AND DATASTORES
    # _______________________________________________________________________________________________
    #

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
        expose_primary_keys: str = "false",
        description: Optional[str] = None,
        evictor_run_periodicity: Optional[int] = 300,
        max_open_prepared_statements: Optional[int] = 50,
        encode_functions: Optional[str] = "false",
        primary_key_metadata_table: Optional[str] = None,
        batch_insert_size: Optional[int] = 1,
        preparedstatements: Optional[str] = "false",
        loose_bbox: Optional[str] = "true",
        estimated_extends: Optional[str] = "true",
        fetch_size: Optional[int] = 1000,
        validate_connections: Optional[str] = "true",
        support_on_the_fly_geometry_simplification: Optional[str] = "true",
        connection_timeout: Optional[int] = 20,
        create_database: Optional[str] = "false",
        min_connections: Optional[int] = 1,
        max_connections: Optional[int] = 10,
        evictor_tests_per_run: Optional[int] = 3,
        test_while_idle: Optional[str] = "true",
        max_connection_idle_time: Optional[int] = 300,
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

        expose_primary_keys: str
        description : str, optional
        evictor_run_periodicity : str
        max_open_prepared_statements : int
        encode_functions : str
        primary_key_metadata_table : str
        batch_insert_size : int
        preparedstatements : str
        loose_bbox : str
        estimated_extends : str
        fetch_size : int
        validate_connections : str
        support_on_the_fly_geometry_simplification : str
        connection_timeout : int
        create_database : str
        min_connections : int
        max_connections : int
        evictor_tests_per_run : int
        test_while_idle : str
        max_connection_idle_time : int


        Notes
        -----
        After creating feature store, you need to publish it. See the layer publish guidline here: https://geoserver-rest.readthedocs.io/en/latest/how_to_use.html#creating-and-publishing-featurestores-and-featurestore-layers
        """
        url = "{}/rest/workspaces/{}/datastores".format(self.service_url, workspace)

        headers = {"content-type": "text/xml"}

        database_connection = """
                <dataStore>
                <name>{}</name>
                <description>{}</description>
                <connectionParameters>
                <entry key="Expose primary keys">{}</entry>
                <entry key="host">{}</entry>
                <entry key="port">{}</entry>
                <entry key="user">{}</entry>
                <entry key="passwd">{}</entry>
                <entry key="dbtype">postgis</entry>
                <entry key="schema">{}</entry>
                <entry key="database">{}</entry>
                <entry key="Evictor run periodicity">{}</entry>
                <entry key="Max open prepared statements">{}</entry>
                <entry key="encode functions">{}</entry>
                <entry key="Primary key metadata table">{}</entry>
                <entry key="Batch insert size">{}</entry>
                <entry key="preparedStatements">{}</entry>
                <entry key="Estimated extends">{}</entry>
                <entry key="fetch size">{}</entry>
                <entry key="validate connections">{}</entry>
                <entry key="Support on the fly geometry simplification">{}</entry>
                <entry key="Connection timeout">{}</entry>
                <entry key="create database">{}</entry>
                <entry key="min connections">{}</entry>
                <entry key="max connections">{}</entry>
                <entry key="Evictor tests per run">{}</entry>
                <entry key="Test while idle">{}</entry>
                <entry key="Max connection idle time">{}</entry>
                <entry key="Loose bbox">{}</entry>
                </connectionParameters>
                </dataStore>
                """.format(
            store_name,
            description,
            expose_primary_keys,
            host,
            port,
            pg_user,
            pg_password,
            schema,
            db,
            evictor_run_periodicity,
            max_open_prepared_statements,
            encode_functions,
            primary_key_metadata_table,
            batch_insert_size,
            preparedstatements,
            estimated_extends,
            fetch_size,
            validate_connections,
            support_on_the_fly_geometry_simplification,
            connection_timeout,
            create_database,
            min_connections,
            max_connections,
            evictor_tests_per_run,
            test_while_idle,
            max_connection_idle_time,
            loose_bbox,
        )

        if overwrite:
            url = "{}/rest/workspaces/{}/datastores/{}".format(
                self.service_url, workspace, store_name
            )

            r = self._requests(
                "put",
                url,
                data=database_connection,
                headers=headers,
            )
        else:
            r = self._requests(
                "post",
                url,
                data=database_connection,
                headers=headers,
            )

        if r.status_code in [200, 201]:
            return "Featurestore created/updated successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

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
        workspace : str, optional default value = "default".
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

        if overwrite:
            url = "{}/rest/workspaces/{}/datastores/{}".format(
                self.service_url, workspace, name
            )
            r = self._requests("put", url, data=data, headers=headers)

        else:
            url = "{}/rest/workspaces/{}/datastores".format(self.service_url, workspace)
            r = requests.post(
                url, data, auth=(self.username, self.password), headers=headers
            )

        if r.status_code in [200, 201]:
            return "Data store created/updated successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

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
            raise GeoserverException(r.status_code, r.content)

    def publish_featurestore(
        self,
        store_name: str,
        pg_table: str,
        workspace: Optional[str] = None,
        title: Optional[str] = None,
        advertised: Optional[bool] = True,
    ):
        """

        Parameters
        ----------
        store_name : str
        pg_table : str
        workspace : str, optional
        title : str, optional
        advertised : bool, optional

        Returns
        -------

        Notes
        -----
        Only user for postgis vector data
        input parameters: specify the name of the table in the postgis database to be published, specify the store,workspace name, and  the Geoserver user name, password and URL
        """
        if workspace is None:
            workspace = "default"
        if title is None:
            title = pg_table

        url = "{}/rest/workspaces/{}/datastores/{}/featuretypes/".format(
            self.service_url, workspace, store_name
        )

        layer_xml = """<featureType>
                    <name>{}</name>
                    <title>{}</title>
                    <advertised>{}</advertised>
                </featureType>""".format(
            pg_table, title, advertised
        )
        headers = {"content-type": "text/xml"}

        r = requests.post(
            url,
            data=layer_xml,
            auth=(self.username, self.password),
            headers=headers,
        )
        if r.status_code == 201:
            return r.status_code
        else:
            raise GeoserverException(r.status_code, r.content)

    def edit_featuretype(
        self,
        store_name: str,
        workspace: Optional[str],
        pg_table: str,
        name: str,
        title: str,
    ):
        """

        Parameters
        ----------
        store_name : str
        workspace : str, optional
        pg_table : str
        name : str
        title : str

        Returns
        -------

        Notes
        -----
        """
        if workspace is None:
            workspace = "default"

        url = "{}/rest/workspaces/{}/datastores/{}/featuretypes/{}.xml".format(
            self.service_url, workspace, store_name, pg_table
        )

        layer_xml = """<featureType>
                    <name>{}</name>
                    <title>{}</title>
                    </featureType>""".format(
            name, title
        )
        headers = {"content-type": "text/xml"}

        r = requests.put(
            url,
            data=layer_xml,
            auth=(self.username, self.password),
            headers=headers,
        )
        if r.status_code == 200:
            return r.status_code
        else:
            raise GeoserverException(r.status_code, r.content)

    def publish_featurestore_sqlview(
        self,
        name: str,
        store_name: str,
        sql: str,
        geom_name: str = "geom",
        geom_type: str = "Geometry",
        srid: Optional[int] = 4326,
        workspace: Optional[str] = None,
    ):
        """

        Parameters
        ----------
        name : str
        store_name : str
        sql : str
        geom_name : str
        geom_type : str
        workspace : str, optional

        """
        if workspace is None:
            workspace = "default"

        layer_xml = """<featureType>
        <name>{0}</name>
        <enabled>true</enabled>
        <namespace>
            <name>{4}</name>
        </namespace>
        <title>{0}</title>
        <srs>EPSG:{5}</srs>
        <metadata>
            <entry key="JDBC_VIRTUAL_TABLE">
                <virtualTable>
                    <name>{0}</name>
                    <sql>{1}</sql>
                    <escapeSql>true</escapeSql>
                    <geometry>
                        <name>{2}</name>
                        <type>{3}</type>
                        <srid>{5}</srid>
                    </geometry>
                </virtualTable>
            </entry>
        </metadata>
        </featureType>""".format(
            name, sql, geom_name, geom_type, workspace, srid
        )

        url = "{}/rest/workspaces/{}/datastores/{}/featuretypes".format(
            self.service_url, workspace, store_name
        )

        headers = {"content-type": "text/xml"}

        r = requests.post(
            url,
            data=layer_xml,
            auth=(self.username, self.password),
            headers=headers,
        )

        if r.status_code == 201:
            return r.status_code
        else:
            raise GeoserverException(r.status_code, r.content)

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
        if r.status_code == 200:
            r_dict = r.json()
            features = [i["name"] for i in r_dict["featureTypes"]["featureType"]]
            return features
        else:
            raise GeoserverException(r.status_code, r.content)

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
        if r.status_code == 200:
            r_dict = r.json()
            attribute = [
                i["name"] for i in r_dict["featureType"]["attributes"]["attribute"]
            ]
            return attribute
        else:
            raise GeoserverException(r.status_code, r.content)

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
        if r.status_code == 200:
            r_dict = r.json()
            return r_dict["dataStore"]
        else:
            raise GeoserverException(r.status_code, r.content)

    def delete_featurestore(
        self, featurestore_name: str, workspace: Optional[str] = None
    ):
        """

        Parameters
        ----------
        featurestore_name : str
        workspace : str, optional

        """
        payload = {"recurse": "true"}
        url = "{}/rest/workspaces/{}/datastores/{}".format(
            self.service_url, workspace, featurestore_name
        )
        if workspace is None:
            url = "{}/datastores/{}".format(self.service_url, featurestore_name)
        r = requests.delete(url, auth=(self.username, self.password), params=payload)

        if r.status_code == 200:
            return "Status code: {}, delete featurestore".format(r.status_code)
        else:
            raise GeoserverException(r.status_code, r.content)

    def delete_coveragestore(
        self, coveragestore_name: str, workspace: Optional[str] = None
    ):
        """

        Parameters
        ----------
        coveragestore_name : str
        workspace : str, optional

        """
        payload = {"recurse": "true"}
        url = "{}/rest/workspaces/{}/coveragestores/{}".format(
            self.service_url, workspace, coveragestore_name
        )

        if workspace is None:
            url = "{}/rest/coveragestores/{}".format(
                self.service_url, coveragestore_name
            )

        r = requests.delete(url, auth=(self.username, self.password), params=payload)

        if r.status_code == 200:
            return "Coverage store deleted successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

    # _______________________________________________________________________________________________
    #
    #      USERS AND USERGROUPS
    # _______________________________________________________________________________________________
    #

    def get_all_users(self, service=None):
        """

        Parameters
        ----------
        service: str, optional

        Query all users in the provided user/group service, else default user/group service is queried
        """
        url = "{}/rest/security/usergroup/".format(self.service_url)
        if service is None:
            url += "users/"
        else:
            url += "service/{}/users/".format(service)

        headers = {"accept": "application/xml"}
        r = requests.get(url, auth=(self.username, self.password), headers=headers)

        if r.status_code == 200:
            return parse(r.content)
        else:
            raise GeoserverException(r.status_code, r.content)

    def create_user(
        self, username: str, password: str, enabled: bool = True, service=None
    ):
        """

        Parameters
        ----------
        username : str
        password: str
        enabled: bool
        service : str, optional

        Add a new user to the provided user/group service
        If no user/group service is provided, then the users is added to default user service
        """
        url = "{}/rest/security/usergroup/".format(self.service_url)
        if service is None:
            url += "users/"
        else:
            url += "service/{}/users/".format(service)

        data = "<user><userName>{}</userName><password>{}</password><enabled>{}</enabled></user>".format(
            username, password, str(enabled).lower()
        )
        headers = {"content-type": "text/xml", "accept": "application/json"}
        r = requests.post(
            url, data, auth=(self.username, self.password), headers=headers
        )

        if r.status_code == 201:
            return "User created successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

    def modify_user(
        self, username: str, new_name=None, new_password=None, enable=None, service=None
    ):
        """

        Parameters
        ----------
        username : str
        new_name : str, optional
        new_password : str, optional
        enable : bool, optional
        service : str, optional

        Modifies a user in the provided user/group service
        If no user/group service is provided, then the user in the default user service is modified
        """
        url = "{}/rest/security/usergroup/".format(self.service_url)
        if service is None:
            url += "user/{}".format(username)
        else:
            url += "service/{}/user/{}".format(service, username)

        modifications = dict()
        if new_name is not None:
            modifications["userName"] = new_name
        if new_password is not None:
            modifications["password"] = new_password
        if enable is not None:
            modifications["enabled"] = enable

        data = unparse({"user": modifications})
        print(url, data)
        headers = {"content-type": "text/xml", "accept": "application/json"}
        r = requests.post(
            url, data, auth=(self.username, self.password), headers=headers
        )

        if r.status_code == 200:
            return "User modified successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

    def delete_user(self, username: str, service=None):
        """

        Parameters
        ----------
        username : str
        user_service : str, optional

        Deletes user from the provided user/group service
        If no user/group service is provided, then the users is deleted from default user service
        """
        url = "{}/rest/security/usergroup/".format(self.service_url)
        if service is None:
            url += "user/{}".format(username)
        else:
            url += "service/{}/user/{}".format(service, username)

        headers = {"accept": "application/json"}
        r = requests.delete(url, auth=(self.username, self.password), headers=headers)

        if r.status_code == 200:
            return "User deleted successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_all_usergroups(self, service=None):
        """

        Parameters
        ----------
        service : str, optional

        Queries all the groups in the given user/group service
        If no user/group service is provided, default user/group service is used
        """
        url = "{}/rest/security/usergroup/".format(self.service_url)
        if service is None:
            url += "groups/"
        else:
            url += "service/{}/groups/".format(service)

        r = requests.get(url, auth=(self.username, self.password))

        if r.status_code == 200:
            return parse(r.content)
        else:
            raise GeoserverException(r.status_code, r.content)

    def create_usergroup(self, group: str, service=None):
        """

        Parameters
        ----------
        group : str
        service : str, optional

        Add a new usergroup to the provided user/group service
        If no user/group service is provided, then the usergroup is added to default user service
        """
        url = "{}/rest/security/usergroup/".format(self.service_url)
        if service is None:
            url += "group/{}".format(group)
        else:
            url += "service/{}/group/{}".format(service, group)
        r = requests.post(url, auth=(self.username, self.password))

        if r.status_code == 201:
            return "Group created successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

    def delete_usergroup(self, group: str, service=None):
        """

        Parameters
        ----------
        group : str
        service : str, optional

        Deletes given usergroup from provided user/group service
        If no user/group service is provided, then the usergroup deleted from default user service
        """
        url = "{}/rest/security/usergroup/".format(self.service_url)
        if service is None:
            url += "group/{}".format(group)
        else:
            url += "service/{}/group/{}".format(service, group)

        r = requests.delete(url, auth=(self.username, self.password))

        if r.status_code == 200:
            return "Group deleted successfully"
        else:
            raise GeoserverException(r.status_code, r.content)
