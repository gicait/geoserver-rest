# inbuilt libraries
import os
from typing import List, Optional, Set, Union, Dict, Iterable, Any
from pathlib import Path

# third-party libraries
import requests
from xmltodict import parse, unparse

# custom functions
from .supports import prepare_zip_file, is_valid_xml, is_surrounded_by_quotes


def _parse_request_options(request_options: Dict[str, Any]):
    """
    Parse request options.

    Parameters
    ----------
    request_options : dict
        The request options to parse.

    Returns
    -------
    dict
        The parsed request options.
    """
    return request_options if request_options is not None else {}


# Custom exceptions.
class GeoserverException(Exception):
    """
    Custom exception for Geoserver errors.

    Parameters
    ----------
    status : int
        The status code of the error.
    message : str
        The error message.
    """
    def __init__(self, status, message):
        self.status = status
        self.message = message
        super().__init__(f"Status : {self.status} - {self.message}")


# call back class for reading the data
class DataProvider:
    """
    Data provider for reading data.

    Parameters
    ----------
    data : str
        The data to be read.
    """
    def __init__(self, data):
        self.data = data
        self.finished = False

    def read_cb(self, size):
        """
        Read callback.

        Parameters
        ----------
        size : int
            The size of the data to read.

        Returns
        -------
        str
            The read data.
        """
        assert len(self.data) <= size
        if not self.finished:
            self.finished = True
            return self.data
        else:
            # Nothing more to read
            return ""


# callback class for reading the files
class FileReader:
    """
    File reader for reading files.

    Parameters
    ----------
    fp : file object
        The file object to read from.
    """
    def __init__(self, fp):
        self.fp = fp

    def read_callback(self, size):
        """
        Read callback.

        Parameters
        ----------
        size : int
            The size of the data to read.

        Returns
        -------
        str
            The read data.
        """
        return self.fp.read(size)


class Geoserver:
    """
    Geoserver class to interact with GeoServer REST API.

    Attributes
    ----------
    service_url : str
        The URL for the GeoServer instance.
    username : str
        Login name for session.
    password: str
        Password for session.
    request_options : dict
        Additional parameters to be sent with each request.
    """

    def __init__(
        self,
        service_url: str = "http://localhost:8080/geoserver",  # default deployment url during installation
        username: str = "admin",  # default username during geoserver installation
        password: str = "geoserver",  # default password during geoserver installation
        request_options: Dict[str, Any] = None  # additional parameters to be sent with each request
    ):
        self.service_url = service_url
        self.username = username
        self.password = password
        self.request_options = request_options if request_options is not None else {}

    def _requests(self,
                  method: str,
                  url: str,
                  **kwargs) -> requests.Response:
        """
        Convenience wrapper to the requests library which automatically handles the authentication, as well as additional options to be passed to each request.

        Parameters
        ----------
        method : str
            Which method to use (`get`, `post`, `put`, `delete`)
        url : str
            URL to which to make the request
        kwargs : dict
            Additional arguments to pass to the request.

        Returns
        -------
        requests.Response
            The response object.
        """

        if method.lower() == "post":
            return requests.post(url, auth=(self.username, self.password), **kwargs, **self.request_options)
        elif method.lower() == "get":
            return requests.get(url, auth=(self.username, self.password), **kwargs, **self.request_options)
        elif method.lower() == "put":
            return requests.put(url, auth=(self.username, self.password), **kwargs, **self.request_options)
        elif method.lower() == "delete":
            return requests.delete(url, auth=(self.username, self.password), **kwargs, **self.request_options)

    # _______________________________________________________________________________________________
    #
    #       GEOSERVER AND SERVER SPECIFIC METHODS
    # _______________________________________________________________________________________________
    #

    def get_manifest(self):
        """
        Returns the manifest of the GeoServer. The manifest is a JSON of all the loaded JARs on the GeoServer server.

        Returns
        -------
        dict
            The manifest of the GeoServer.
        """
        url = "{}/rest/about/manifest.json".format(self.service_url)
        r = self._requests("get", url)
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_version(self):
        """
        Returns the version of the GeoServer as JSON. It contains only the details of the high level components: GeoServer, GeoTools, and GeoWebCache.

        Returns
        -------
        dict
            The version information of the GeoServer.
        """
        url = "{}/rest/about/version.json".format(self.service_url)
        r = self._requests("get", url)
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_status(self):
        """
        Returns the status of the GeoServer. It shows the status details of all installed and configured modules.

        Returns
        -------
        dict
            The status of the GeoServer.
        """
        url = "{}/rest/about/status.json".format(self.service_url)
        r = self._requests("get", url)
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_system_status(self):
        """
        Returns the system status of the GeoServer. It returns a list of system-level information. Major operating systems (Linux, Windows, and MacOS) are supported out of the box.

        Returns
        -------
        dict
            The system status of the GeoServer.
        """
        url = "{}/rest/about/system-status.json".format(self.service_url)
        r = self._requests("get", url)
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def reload(self):
        """
        Reloads the GeoServer catalog and configuration from disk.

        This operation is used in cases where an external tool has modified the on-disk configuration. This operation will also force GeoServer to drop any internal caches and reconnect to all data stores.

        Returns
        -------
        str
            The status code of the reload operation.
        """
        url = "{}/rest/reload".format(self.service_url)
        r = self._requests("post", url)
        if r.status_code == 200:
            return "Status code: {}".format(r.status_code)
        else:
            raise GeoserverException(r.status_code, r.content)

    def reset(self):
        """
        Resets all store, raster, and schema caches. This operation is used to force GeoServer to drop all caches and store connections and reconnect to each of them the next time they are needed by a request. This is useful in case the stores themselves cache some information about the data structures they manage that may have changed in the meantime.

        Returns
        -------
        str
            The status code of the reset operation.
        """
        url = "{}/rest/reset".format(self.service_url)
        r = self._requests("post", url)
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

        Returns
        -------
        dict
            The default workspace.
        """
        url = "{}/rest/workspaces/default".format(self.service_url)
        r = self._requests("get", url)

        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_workspace(self, workspace):
        """
        Get the name of a workspace if it exists.

        Parameters
        ----------
        workspace : str
            The name of the workspace.

        Returns
        -------
        dict
            The workspace information.
        """
        url = "{}/rest/workspaces/{}.json".format(self.service_url, workspace)
        r = self._requests("get", url, params={"recurse": "true"})

        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_workspaces(self):
        """
        Returns all the workspaces.

        Returns
        -------
        dict
            All the workspaces.
        """
        url = "{}/rest/workspaces".format(self.service_url)
        r = self._requests("get", url)

        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def set_default_workspace(self, workspace: str):
        """
        Set the default workspace.

        Parameters
        ----------
        workspace : str
            The name of the workspace to set as default.

        Returns
        -------
        str
            The status code of the operation.
        """
        url = "{}/rest/workspaces/default".format(self.service_url)
        data = "<workspace><name>{}</name></workspace>".format(workspace)

        r = self._requests(
            "put",
            url,
            data=data,
            headers={"content-type": "text/xml"}
        )

        if r.status_code == 200:
            return "Status code: {}, default workspace {} set!".format(
                r.status_code, workspace
            )
        else:
            raise GeoserverException(r.status_code, r.content)

    def create_workspace(self, workspace: str):
        """
        Create a new workspace in GeoServer. The GeoServer workspace URL will be the same as the name of the workspace.

        Parameters
        ----------
        workspace : str
            The name of the workspace to create.

        Returns
        -------
        str
            The status code and message of the operation.
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
        Delete a workspace.

        Parameters
        ----------
        workspace : str
            The name of the workspace to delete.

        Returns
        -------
        str
            The status code and message of the operation.
        """
        payload = {"recurse": "true"}
        url = "{}/rest/workspaces/{}".format(self.service_url, workspace)
        r = self._requests("delete", url, params=payload)

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
        Return the data store in a given workspace. If workspace is not provided, it will take the default workspace.

        Parameters
        ----------
        store_name : str
            The name of the data store.
        workspace : str, optional
            The name of the workspace.

        Returns
        -------
        dict
            The data store information.
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
        List all data stores in a workspace. If workspace is not provided, it will list all the datastores inside the default workspace.

        Parameters
        ----------
        workspace : str, optional
            The name of the workspace.

        Returns
        -------
        dict
            The list of data stores.
        """
        if workspace is None:
            workspace = "default"

        url = "{}/rest/workspaces/{}/datastores.json".format(
            self.service_url, workspace
        )
        r = self._requests("get", url)
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

        Parameters
        ----------
        coveragestore_name : str
            The name of the coverage store.
        workspace : str, optional
            The name of the workspace.

        Returns
        -------
        dict
            The coverage store information.
        """
        payload = {"recurse": "true"}
        if workspace is None:
            workspace = "default"
        url = "{}/rest/workspaces/{}/coveragestores/{}.json".format(
            self.service_url, workspace, coveragestore_name
        )
        r = self._requests(method="get", url=url, params=payload)

        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_coveragestores(self, workspace: str = None):
        """
        Returns all the coverage stores inside a specific workspace.

        Parameters
        ----------
        workspace : str, optional
            The name of the workspace.

        Returns
        -------
        dict
            The list of coverage stores.
        """
        if workspace is None:
            workspace = "default"

        url = "{}/rest/workspaces/{}/coveragestores".format(self.service_url, workspace)
        r = self._requests("get", url)
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
        Creates the coverage store; Data will be uploaded to the server.

        Parameters
        ----------
        path : str
            The path to the file.
        workspace : str, optional
            The name of the workspace.
        layer_name : str, optional
            The name of the coverage store. If not provided, parsed from the file name.
        file_type : str
            The type of the file.
        content_type : str
            The content type of the file.

        Returns
        -------
        dict
            The response from the server.

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
        Create time dimension in coverage store to publish time series in GeoServer.

        Parameters
        ----------
        store_name : str, optional
            The name of the coverage store.
        workspace : str, optional
            The name of the workspace.
        presentation : str, optional
            The presentation style.
        units : str, optional
            The units of the time dimension.
        default_value : str, optional
            The default value of the time dimension.
        content_type : str
            The content type of the request.

        Returns
        -------
        dict
            The response from the server.

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

        Parameters
        ----------
        layer_name : str
            The name of the layer.
        workspace : str, optional
            The name of the workspace.

        Returns
        -------
        dict
            The layer information.
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
        Get all the layers from GeoServer. If workspace is None, it will list all the layers from GeoServer.

        Parameters
        ----------
        workspace : str, optional
            The name of the workspace.

        Returns
        -------
        dict
            The list of layers.
        """
        url = "{}/rest/layers".format(self.service_url)

        if workspace is not None:
            url = "{}/rest/workspaces/{}/layers".format(self.service_url, workspace)
        r = self._requests("get", url)
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def delete_layer(self, layer_name: str, workspace: Optional[str] = None):
        """
        Delete a layer.

        Parameters
        ----------
        layer_name : str
            The name of the layer to delete.
        workspace : str, optional
            The name of the workspace.

        Returns
        -------
        str
            The status code and message of the operation.
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
        Returns all the layer groups from GeoServer. If workspace is None, it will list all the layer groups from GeoServer.

        Parameters
        ----------
        workspace : str, optional
            The name of the workspace.

        Returns
        -------
        dict
            The list of layer groups.

        Notes
        -----
        If workspace is None, it will list all the layer groups from geoserver.
        """
        url = "{}/rest/layergroups".format(self.service_url)

        if workspace is not None:
            url = "{}/rest/workspaces/{}/layergroups".format(
                self.service_url, workspace
            )
        r = self._requests("get", url)
        if r.status_code == 200:
            return r.json()
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_layergroup(self, layer_name: str, workspace: Optional[str] = None):
        """
        Returns the layer group by layer group name.

        Parameters
        ----------
        layer_name : str
            The name of the layer group.
        workspace : str, optional
            The name of the workspace.

        Returns
        -------
        dict
            The layer group information.
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
            The name of the layer group.
        mode : str
            The mode of the layer group.
        title : str
            The title of the layer group.
        abstract_text : str
            The abstract text of the layer group.
        layers : list
            The list of layers in the layer group.
        workspace : str, optional
            The name of the workspace.
        formats : str, optional
            The format of the layer group.
        metadata : list, optional
            The metadata of the layer group.
        keywords : list, optional
            The keywords of the layer group.

        Returns
        -------
        str
            The URL of the created layer group.

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
        ), "Metadata must be of type List of dict:[{'about':'geoserver rest data metadata','content_url':'link to content url'}]"
        assert isinstance(
            keywords, list
        ), "Keywords must be of type List:['keyword1','keyword2'...]"
        assert isinstance(
            layers, list
        ), "Layers must be of type List:['layer1','layer2'...]"

        if workspace:
            assert isinstance(workspace, str), "Workspace must be of type String:''"
            # check if the workspace is valid in GeoServer
            if self.get_workspace(workspace) is None:
                raise Exception("Workspace is not valid in GeoServer Instance")

        supported_modes: Set = {
            "single",
            "opaque",
            "named",
            "container",
            "eo",
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

        # check if it already exist in GeoServer
        try:
            existing_layergroup = self.get_layergroup(name, workspace=workspace)
        except GeoserverException:
            existing_layergroup = None

        if existing_layergroup is not None:
            raise Exception(f"Layergroup: {name} already exist in GeoServer instance")

        if len(layers) == 0:
            raise Exception("No layer provided!")
        else:
            for layer in layers:
                # check if it is valid in geoserver
                try:
                    # Layer check
                    self.get_layer(
                        layer_name=layer,
                        workspace=workspace if workspace is not None else None,
                    )
                except GeoserverException:
                    try:
                        # Layer group check
                        self.get_layergroup(
                            layer_name=layer,
                            workspace=workspace if workspace is not None else None,
                        )
                    except GeoserverException:
                        raise Exception(
                            f"Layer: {layer} is not a valid layer in the GeoServer instance"
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
            published_type = "layer"
            try:
                # Layer check
                self.get_layer(
                    layer_name=layer,
                    workspace=workspace if workspace is not None else None,
                )
            except GeoserverException: # It's a layer group
                published_type = "layerGroup"

            layers_xml_list.append(
                f"""<published type="{published_type}">
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
        layergroup_name: str
            The name of the layergroup to update.
        title : str, optional
            The new title for the layergroup.
        abstract_text : str, optional
            The new abstract text for the layergroup.
        formats : str, optional
            The format of the response. Default is "html".
        metadata : list of dict, optional
            List of metadata entries where each entry is a dictionary with "about" and "content_url" keys.
        keywords : list of str, optional
            List of keywords associated with the layergroup.

        Returns
        -------
        str
            A success message indicating that the layergroup was updated.

        Raises
        ------
        GeoserverException
            If there is an issue updating the layergroup.
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
            keywords_xml: str = f"<keywords>{''.join(['{}'] * len(keyword_xml_list)).format(*keyword_xml_list)}</keywords>"
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
        layergroup_name: str
            The name of the layer group to be deleted.
        workspace: str, optional
            The workspace the layergroup is located in.

        Returns
        -------
        str
            A success message indicating that the layer group was deleted.

        Raises
        ------
        GeoserverException
            If there is an issue deleting the layergroup.
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
        layer_name: str
            The name of the layer.
        layer_workspace: str
            The workspace the layer is located in.
        layergroup_workspace: str, optional
            The workspace the layergroup is located in.
        layergroup_name: str
            The name of the layer group.
        layergroup_workspace: str, optional
            The workspace the layergroup is located in.

        Returns
        -------
        None

        Raises
        ------
        GeoserverException
            If there is an issue adding the layer to the layergroup.
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
        layer_name: str
            The name of the layer.
        layer_workspace: str
            The workspace the layer is located in.
        layergroup_workspace: str, optional
            The workspace the layergroup is located in.
        layergroup_name: str
            The name of the layer group.
        layergroup_workspace: str, optional
            The workspace the layergroup is located in.

        Returns
        -------
        None

        Raises
        ------
        GeoserverException
            If there is an issue removing the layer from the layergroup.
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
        Helper function for add_layer_to_layergroup and remove_layer_from_layergroup.

        Parameters
        ----------
        publishables: list
            List of publishable layers.
        styles: list
            List of styles associated with the publishable layers.

        Returns
        -------
        str
            Formatted XML request body for PUT layergroup.
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

        Parameters
        ----------
        style_name: str
            The name of the style.
        workspace: str, optional
            The workspace the style is located in.

        Returns
        -------
        dict
            A dictionary representation of the style.

        Raises
        ------
        GeoserverException
            If there is an issue retrieving the style.
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

        Parameters
        ----------
        workspace: str, optional
            The workspace to filter the styles by.

        Returns
        -------
        dict
            A dictionary containing all the styles.

        Raises
        ------
        GeoserverException
            If there is an issue retrieving the styles.
        """
        url = "{}/rest/styles.json".format(self.service_url)

        if workspace is not None:
            url = "{}/rest/workspaces/{}/styles.json".format(
                self.service_url, workspace
            )
        r = self._requests("get", url)
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
        Uploads a style file to geoserver.

        Parameters
        ----------
        path : str
            Path to the style file or XML string.
        name : str, optional
            The name of the style. If None, the name is parsed from the file name.
        workspace : str, optional
            The workspace to upload the style to.
        sld_version : str, optional
            The version of the SLD. Default is "1.0.0".

        Returns
        -------
        int
            The status code of the request.

        Raises
        ------
        GeoserverException
            If there is an issue uploading the style.

        Notes
        -----
        The name of the style file will be, sld_name:workspace
        This function will create the style file in a specified workspace.
        `path` can either be the path to the SLD file itself, or a string containing valid XML to be used for the style
        Inputs: path to the sld_file or the contents of an SLD file itself, workspace,
        """
        if name is None:
            name = os.path.basename(path)
            f = name.split(".")
            if len(f) > 0:
                name = f[0]

        if is_valid_xml(path):
            # path is actually just the xml itself
            xml = path
        elif Path(path).exists():
            # path is pointing to an existing file
            with open(path, "rb") as f:
                xml = f.read()
        else:
            # path is non-existing file or not valid xml
            raise ValueError("`path` must be either a path to a style file, or a valid XML string.")

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
            r_sld = self._requests(method="put", url=url + "/" + name, data=xml, headers=header_sld)

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
            opacity: float = 1,
    ):
        """
        Dynamically create style for raster.

        Parameters
        ----------
        raster_path : str
            Path to the raster file.
        style_name : str, optional
            The name of the style. If None, the name is parsed from the raster file name.
        workspace : str
            The workspace to create the style in.
        color_ramp : str
            The color ramp to use.
        cmap_type : str
            The type of color map.
        number_of_classes : int
            The number of classes.
        opacity : float
            The opacity of the style.

        Returns
        -------
        int
            The status code of the request.

        Raises
        ------
        GeoserverException
            If there is an issue creating the style.

        Notes
        -----
        The name of the style file will be, rasterName:workspace
        This function will dynamically create the style file for raster.
        Inputs: name of file, workspace, cmap_type (two options: values, range), ncolors: determines the number of class, min for minimum value of the raster, max for the max value of raster
        """

        from .Calculation_gdal import raster_value
        from .Style import coverage_style_xml

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
            opacity,
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
                r_sld = self._requests(method="put", url=url + "/" + style_name, data=f.read(), headers=header_sld)

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
        """
        Dynamically create categorized style for postgis geometry,

        Parameters
        ----------
        style_name : str
            The name of the style.
        column_name : str
            The column name to base the style on.
        column_distinct_values
            The distinct values in the column.
        workspace : str
            The workspace to create the style in.
        color_ramp : str
            The color ramp to use.
        geom_type : str
            The geometry type (point, line, polygon).

        Returns
        -------
        int
            The status code of the request.

        Raises
        ------
        GeoserverException
            If there is an issue creating the style.

        Notes
        -----

        The data type must be point, line or polygon
        Inputs: column_name (based on which column style should be generated), workspace,
        color_or_ramp (color should be provided in hex code or the color ramp name, geom_type(point, line, polygon), outline_color(hex_color))
        """
        
        from .Style import catagorize_xml

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
            width: str = "2",
            geom_type: str = "polygon",
            workspace: Optional[str] = None,
    ):
        """
        Dynamically creates the outline style for postgis geometry

        Parameters
        ----------
        style_name : str
            The name of the style.
        color : str
            The color of the outline.
        geom_type : str
            The geometry type (point, line, polygon).
        workspace : str, optional
            The workspace to create the style in.

        Returns
        -------
        int
            The status code of the request.

        Raises
        ------
        GeoserverException
            If there is an issue creating the style.

        Notes
        -----
        The geometry type must be point, line or polygon
        Inputs: style_name (name of the style file in geoserver), workspace, color (style color)
        """

        from .Style import outline_only_xml

        outline_only_xml(color, width, geom_type)

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
        """
        Dynamically creates the classified style for postgis geometries.

        Parameters
        ----------
        style_name : str
            The name of the style.
        column_name : str
            The column name to base the style on.
        column_distinct_values
            The distinct values in the column.
        workspace : str, optional
            The workspace to create the style in.
        color_ramp : str
            The color ramp to use.
        geom_type : str
            The geometry type (point, line, polygon).

        Returns
        -------
        int
            The status code of the request.

        Raises
        ------
        GeoserverException
            If there is an issue creating the style.

        Notes
        -----
        The data type must be point, line or polygon
        Inputs: column_name (based on which column style should be generated), workspace,
        color_or_ramp (color should be provided in hex code or the color ramp name, geom_type(point, line, polygon), outline_color(hex_color))
        """

        from .Style import classified_xml
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
        """
        Publish a raster file to geoserver.

        Parameters
        ----------
        layer_name : str
            The name of the layer.
        style_name : str
            The name of the style.
        workspace : str
            The workspace the layer is located in.

        Returns
        -------
        int
            The status code of the request.

        Raises
        ------
        GeoserverException
            If there is an issue publishing the style.

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
        Delete a style from the geoserver.

        Parameters
        ----------
        style_name : str
            The name of the style.
        workspace : str, optional
            The workspace the style is located in.

        Returns
        -------
        str
            A success message indicating that the style was deleted.

        Raises
        ------
        GeoserverException
            If there is an issue deleting the style.
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
            The name of the feature store.
        workspace : str, optional
            The workspace to create the feature store in.
        db : str
            The database type. Default is "postgres".
        host : str
            The database host. Default is "localhost".
        port : int
            The database port. Default is 5432.
        schema : str
            The database schema. Default is "public".
        pg_user : str
            The database user. Default is "postgres".
        pg_password : str
            The database password. Default is "admin".
        overwrite : bool
            Whether to overwrite the existing feature store.
        expose_primary_keys : str
            Whether to expose primary keys. Default is "false".
        description : str, optional
            The description of the feature store.
        evictor_run_periodicity : int, optional
            The periodicity of the evictor run.
        max_open_prepared_statements : int, optional
            The maximum number of open prepared statements.
        encode_functions : str, optional
            Whether to encode functions. Default is "false".
        primary_key_metadata_table : str, optional
            The primary key metadata table.
        batch_insert_size : int, optional
            The batch insert size. Default is 1.
        preparedstatements : str, optional
            Whether to use prepared statements. Default is "false".
        loose_bbox : str, optional
            Whether to use loose bounding boxes. Default is "true".
        estimated_extends : str, optional
            Whether to use estimated extends. Default is "true".
        fetch_size : int, optional
            The fetch size. Default is 1000.
        validate_connections : str, optional
            Whether to validate connections. Default is "true".
        support_on_the_fly_geometry_simplification : str, optional
            Whether to support on-the-fly geometry simplification. Default is "true".
        connection_timeout : int, optional
            The connection timeout. Default is 20.
        create_database : str, optional
            Whether to create the database. Default is "false".
        min_connections : int, optional
            The minimum number of connections. Default is 1.
        max_connections : int, optional
            The maximum number of connections. Default is 10.
        evictor_tests_per_run : int, optional
            The number of evictor tests per run.
        test_while_idle : str, optional
            Whether to test while idle. Default is "true".
        max_connection_idle_time : int, optional
            The maximum connection idle time. Default is 300.

        Returns
        -------
        str
            A success message indicating that the feature store was created/updated.

        Raises
        ------
        GeoserverException
            If there is an issue creating/updating the feature store.

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
            Name of datastore to be created. After creating the datastore, you need to publish it by using publish_featurestore function.
        path : str
            Path to shapefile (.shp) file, GeoPackage (.gpkg) file, WFS url
            (e.g. http://localhost:8080/geoserver/wfs?request=GetCapabilities) or directory containing shapefiles.
        workspace : str, optional
            The workspace to create the datastore in. Default is "default".
        overwrite : bool
            Whether to overwrite the existing datastore.

        Returns
        -------
        str
            A success message indicating that the datastore was created/updated.

        Raises
        ------
        GeoserverException
            If there is an issue creating/updating the datastore.

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
            r = self._requests(method="post", url=url, data=data, headers=headers)

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
            The file extension of the shapefile. Default is "shp".

        Returns
        -------
        str
            A success message indicating that the shapefile datastore was created.

        Raises
        ------
        GeoserverException
            If there is an issue creating the shapefile datastore.

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
            r = self._requests("put", url, data=f.read(), headers=headers)
        if r.status_code in [200, 201, 202]:
            return "The shapefile datastore created successfully!"
        else:
            raise GeoserverException(r.status_code, r.content)

    def create_gpkg_datastore(
            self,
            path: str,
            store_name: Optional[str] = None,
            workspace: Optional[str] = None,
            file_extension: str = "gpkg",
    ):
        """
        Create datastore for a geopackage.

        Parameters
        ----------
        path : str
            Path to the geopackage file.
        store_name : str, optional
            Name of store to be created. If None, parses from the filename.
        workspace: str, optional
            Name of workspace to be used. Default: "default".
        file_extension : str
            The file extension of the geopackage. Default is "gpkg".

        Returns
        -------
        str
            A success message indicating that the geopackage datastore was created.

        Raises
        ------
        GeoserverException
            If there is an issue creating the geopackage datastore.

        Notes
        -----
        The layer name will be assigned according to the layer name in the geopackage.
        If the layer already exist it will be updated.
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
            "Content-type": "application/x-sqlite3",
            "Accept": "application/json",
        }

        url = "{0}/rest/workspaces/{1}/datastores/{2}/file.{3}?filename={2}".format(
            self.service_url, workspace, store_name, file_extension
        )

        with open(path, "rb") as f:
            r = self._requests("put", url, data=f.read(), headers=headers)

        if r.status_code in [200, 201, 202]:
            return "The geopackage datastore created successfully!"
        else:
            raise GeoserverException(r.status_code, r.content)

    def publish_featurestore(
            self,
            store_name: str,
            pg_table: str,
            workspace: Optional[str] = None,
            title: Optional[str] = None,
            advertised: Optional[bool] = True,
            abstract: Optional[str] = None,
            keywords: Optional[List[str]] = None,
            cqlfilter: Optional[str] = None
    ) -> int:
        """
        Publish a featurestore to geoserver.

        Parameters
        ----------
        store_name : str
            The name of the featurestore.
        pg_table : str
            The name of the PostgreSQL table.
        workspace : str, optional
            The workspace to publish the featurestore in. Default is "default".
        title : str, optional
            The title of the featurestore. If None, the table name is used.
        advertised : bool, optional
            Whether to advertise the featurestore. Default is True.
        abstract : str, optional
            The abstract of the featurestore.
        keywords : list of str, optional
            List of keywords associated with the featurestore.
        cqlfilter : str, optional
            The CQL filter for the featurestore.

        Returns
        -------
        int
            The status code of the request.

        Raises
        ------
        GeoserverException
            If there is an issue publishing the featurestore.

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

        abstract_xml = f"<abstract>{abstract}</abstract>" if abstract else ""
        keywords_xml = ""
        if keywords:
            keywords_xml = "<keywords>"
            for keyword in keywords:
                keywords_xml += f"<string>{keyword}</string>"
            keywords_xml += "</keywords>"

        cqlfilter_xml = f"<cqlFilter>{cqlfilter}</cqlFilter>" if cqlfilter else ""
        layer_xml = f"""<featureType>
                    <name>{pg_table}</name>
                    <title>{title}</title>
                    <advertised>{advertised}</advertised>
                    {abstract_xml}
                    {keywords_xml}
                    {cqlfilter_xml}
                </featureType>"""
        headers = {"content-type": "text/xml"}

        r = self._requests("post", url, data=layer_xml, headers=headers)

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
            abstract: Optional[str] = None,
            keywords: Optional[List[str]] = None,
            recalculate: Optional[str] = None
    ) -> int:
        """
        Edit a featuretype in the geoserver.

        Parameters
        ----------
        recalculate : str, optional
            Recalculate param. Can be: empty string, nativebbox and nativebbox,latlonbbox.
        store_name : str
            The name of the feature store.
        workspace : str, optional
            The workspace of the feature store.
        pg_table : str
            The name of the PostgreSQL table.
        name : str
            The name of the feature type.
        title : str
            The title of the feature type.
        abstract : str, optional
            The abstract of the feature type.
        keywords : list of str, optional
            List of keywords associated with the feature type.

        Returns
        -------
        int
            The status code of the request.

        Raises
        ------
        GeoserverException
            If there is an issue editing the feature type.
        """
        if workspace is None:
            workspace = "default"

        recalculate_param = f"?recalculate={recalculate}" if recalculate else ""

        url = "{}/rest/workspaces/{}/datastores/{}/featuretypes/{}.xml{}".format(
            self.service_url, workspace, store_name, pg_table, recalculate_param
        )

        # Create XML for abstract and keywords
        abstract_xml = f"<abstract>{abstract}</abstract>" if abstract else ""
        keywords_xml = ""
        if keywords:
            keywords_xml = "<keywords>"
            for keyword in keywords:
                keywords_xml += f"<string>{keyword}</string>"
            keywords_xml += "</keywords>"

        layer_xml = f"""<featureType>
                    <name>{name}</name>
                    <title>{title}</title>
                    {abstract_xml}{keywords_xml}
                    </featureType>"""
        headers = {"content-type": "text/xml"}

        r = self._requests("put", url, data=layer_xml, headers=headers)

        if r.status_code == 200:
            return r.status_code
        else:
            raise GeoserverException(r.status_code, r.content)

    def publish_featurestore_sqlview(
            self,
            name: str,
            store_name: str,
            sql: str,
            parameters: Optional[Iterable[Dict]] = None,
            key_column: Optional[str] = None,
            geom_name: str = "geom",
            geom_type: str = "Geometry",
            srid: Optional[int] = 4326,
            workspace: Optional[str] = None,
    ) -> int:
        """
        Publishes an SQL query as a layer, optionally with parameters.

        Parameters
        ----------
        name : str
            The name of the SQL view.
        store_name : str
            The name of the feature store.
        sql : str
            The SQL query.
        parameters : iterable of dict, optional
            List of parameters for the SQL query.
        key_column : str, optional
            The key column.
        geom_name : str, optional
            The name of the geometry column.
        geom_type : str, optional
            The type of the geometry column.
        srid : int, optional
            The spatial reference ID. Default is 4326.
        workspace : str, optional
            The workspace to publish the SQL view in. Default is "default".

        Returns
        -------
        int
            The status code of the request.

        Raises
        ------
        GeoserverException
            If there is an issue publishing the SQL view.

                Notes
        -----
        With regards to SQL view parameters, it is advised to read the relevant section from the geoserver docs:
        https://docs.geoserver.org/main/en/user/data/database/sqlview.html#parameterizing-sql-views

        An integer-based parameter must have a default value

        You should be VERY careful with the `regexp_validator`, as it can open you to SQL injection attacks. If you do
        not supply one for a parameter, it will use the geoserver default `^[\w\d\s]+$`.

        The `parameters` iterable must contain dictionaries with this structure:

        ```
        {
          "name": "<name of parameter (required)>"
          "regexpValidator": "<string containing regex validator> (optional)"
          "defaultValue" : "<default value of parameter if not specified (required only for non-string parameters)>"
        }
        ```
        """
        if workspace is None:
            workspace = "default"

        # issue #87
        if key_column is not None:
            key_column_xml = """<keyColumn>{}</keyColumn>""".format(key_column)

        else:
            key_column_xml = """"""

        parameters_xml = ""
        if parameters is not None:
            for parameter in parameters:

                # non-string parameters MUST have a default value supplied
                if not is_surrounded_by_quotes(sql, parameter["name"]) and not "defaultValue" in parameter:
                    raise ValueError(f"Parameter `{parameter['name']}` appears to be a non-string in the supplied query"
                                     ", but does not have a default value specified. You must supply a default value "
                                     "for non-string parameters using the `defaultValue` key.")

                param_name = parameter.get("name", "")
                default_value = parameter.get("defaultValue", "")
                regexp_validator = parameter.get("regexpValidator", r"^[\w\d\s]+$")
                parameters_xml += (f"""
                    <parameter>
                        <name>{param_name}</name>
                        <defaultValue>{default_value}</defaultValue>
                        <regexpValidator>{regexp_validator}</regexpValidator>
                    </parameter>\n
                """.strip())

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
                    </geometry>{6}
                    {7}
                </virtualTable>
            </entry>
        </metadata>
        </featureType>""".format(
            name, sql, geom_name, geom_type, workspace, srid, key_column_xml, parameters_xml
        )

        # rest API url
        url = "{}/rest/workspaces/{}/datastores/{}/featuretypes".format(
            self.service_url, workspace, store_name
        )

        # headers
        headers = {"content-type": "text/xml"}

        # request
        r = self._requests("post", url, data=layer_xml, headers=headers)

        if r.status_code == 201:
            return r.status_code
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_featuretypes(self, workspace: str = None, store_name: str = None) -> List[str]:
        """
        Get feature types from the geoserver.

        Parameters
        ----------
        workspace : str
            The workspace to get the feature types from.
        store_name : str
            The name of the feature store.

        Returns
        -------
        list of str
            A list of feature types.

        Raises
        ------
        GeoserverException
            If there is an issue getting the feature types.
        """
        url = "{}/rest/workspaces/{}/datastores/{}/featuretypes.json".format(
            self.service_url, workspace, store_name
        )
        r = self._requests("get", url)
        if r.status_code == 200:
            r_dict = r.json()
            features = [i["name"] for i in r_dict["featureTypes"]["featureType"]]
            return features
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_feature_attribute(
            self, feature_type_name: str, workspace: str, store_name: str
    ) -> List[str]:
        """
        Get feature attributes from the geoserver.

        Parameters
        ----------
        feature_type_name : str
            The name of the feature type.
        workspace : str
            The workspace of the feature store.
        store_name : str
            The name of the feature store.

        Returns
        -------
        list of str
            A list of feature attributes.

        Raises
        ------
        GeoserverException
            If there is an issue getting the feature attributes.
        """
        url = "{}/rest/workspaces/{}/datastores/{}/featuretypes/{}.json".format(
            self.service_url, workspace, store_name, feature_type_name
        )
        r = self._requests("get", url)
        if r.status_code == 200:
            r_dict = r.json()
            attribute = [
                i["name"] for i in r_dict["featureType"]["attributes"]["attribute"]
            ]
            return attribute
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_featurestore(self, store_name: str, workspace: str) -> dict:
        """
        Get a featurestore from the geoserver.

        Parameters
        ----------
        store_name : str
            The name of the feature store.
        workspace : str
            The workspace of the feature store.

        Returns
        -------
        dict
            A dictionary representation of the feature store.

        Raises
        ------
        GeoserverException
            If there is an issue getting the feature store.
        """
        url = "{}/rest/workspaces/{}/datastores/{}".format(
            self.service_url, workspace, store_name
        )
        r = self._requests("get", url)
        if r.status_code == 200:
            r_dict = r.json()
            return r_dict["dataStore"]
        else:
            raise GeoserverException(r.status_code, r.content)

    def delete_featurestore(
            self, featurestore_name: str, workspace: Optional[str] = None
    ) -> str:
        """
        Delete a featurestore from the geoserver.

        Parameters
        ----------
        featurestore_name : str
            The name of the featurestore.
        workspace : str, optional
            The workspace of the featurestore.

        Returns
        -------
        str
            A success message indicating that the featurestore was deleted.

        Raises
        ------
        GeoserverException
            If there is an issue deleting the featurestore.
        """
        payload = {"recurse": "true"}
        url = "{}/rest/workspaces/{}/datastores/{}".format(
            self.service_url, workspace, featurestore_name
        )
        if workspace is None:
            url = "{}/datastores/{}".format(self.service_url, featurestore_name)
        r = self._requests("delete", url, params=payload)

        if r.status_code == 200:
            return "Status code: {}, delete featurestore".format(r.status_code)
        else:
            raise GeoserverException(r.status_code, r.content)

    def delete_coveragestore(
            self, coveragestore_name: str, workspace: Optional[str] = None
    ) -> str:
        """
        Delete a coveragestore from the geoserver.

        Parameters
        ----------
        coveragestore_name : str
            The name of the coveragestore.
        workspace : str, optional
            The workspace of the coveragestore.

        Returns
        -------
        str
            A success message indicating that the coveragestore was deleted.

        Raises
        ------
        GeoserverException
            If there is an issue deleting the coveragestore.
        """
        payload = {"recurse": "true"}
        url = "{}/rest/workspaces/{}/coveragestores/{}".format(
            self.service_url, workspace, coveragestore_name
        )

        if workspace is None:
            url = "{}/rest/coveragestores/{}".format(
                self.service_url, coveragestore_name
            )

        r = self._requests("delete", url, params=payload)

        if r.status_code == 200:
            return "Coverage store deleted successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

    # _______________________________________________________________________________________________
    #
    #      USERS AND USERGROUPS
    # _______________________________________________________________________________________________
    #

    def get_all_users(self, service=None) -> dict:
        """
        Query all users in the provided user/group service, else default user/group service is queried.

        Parameters
        ----------
        service: str, optional
            The user/group service to query.

        Returns
        -------
        dict
            A dictionary containing all users.

        Raises
        ------
        GeoserverException
            If there is an issue getting the users.
        """
        url = "{}/rest/security/usergroup/".format(self.service_url)
        if service is None:
            url += "users/"
        else:
            url += "service/{}/users/".format(service)

        headers = {"accept": "application/xml"}
        r = self._requests("get", url, headers=headers)

        if r.status_code == 200:
            return parse(r.content)
        else:
            raise GeoserverException(r.status_code, r.content)

    def create_user(
            self, username: str, password: str, enabled: bool = True, service=None
    ) -> str:
        """
        Add a new user to the provided user/group service.

        Parameters
        ----------
        username : str
            The username of the new user.
        password: str
            The password of the new user.
        enabled: bool
            Whether the new user is enabled.
        service : str, optional
            The user/group service to add the user to.

        Returns
        -------
        str
            A success message indicating that the user was created.

        Raises
        ------
        GeoserverException
            If there is an issue creating the user.
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
        r = self._requests("post", url, data=data, headers=headers)

        if r.status_code == 201:
            return "User created successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

    def modify_user(
            self, username: str, new_name=None, new_password=None, enable=None, service=None
    ) -> str:
        """
        Modifies a user in the provided user/group service.

        Parameters
        ----------
        username : str
            The username of the user to modify.
        new_name : str, optional
            The new username.
        new_password : str, optional
            The new password.
        enable : bool, optional
            Whether the user is enabled.
        service : str, optional
            The user/group service to modify the user in.

        Returns
        -------
        str
            A success message indicating that the user was modified.

        Raises
        ------
        GeoserverException
            If there is an issue modifying the user.
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
        r = self._requests("post", url, data=data, headers=headers)

        if r.status_code == 200:
            return "User modified successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

    def delete_user(self, username: str, service=None) -> str:
        """
        Deletes user from the provided user/group service.

        Parameters
        ----------
        username : str
            The username of the user to delete.
        service : str, optional
            The user/group service to delete the user from.

        Returns
        -------
        str
            A success message indicating that the user was deleted.

        Raises
        ------
        GeoserverException
            If there is an issue deleting the user.
        """
        url = "{}/rest/security/usergroup/".format(self.service_url)
        if service is None:
            url += "user/{}".format(username)
        else:
            url += "service/{}/user/{}".format(service, username)

        headers = {"accept": "application/json"}
        r = self._requests("delete", url, headers=headers)

        if r.status_code == 200:
            return "User deleted successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

    def get_all_usergroups(self, service=None) -> dict:
        """
        Queries all the groups in the given user/group service.

        Parameters
        ----------
        service : str, optional
            The user/group service to query.

        Returns
        -------
        dict
            A dictionary containing all user groups.

        Raises
        ------
        GeoserverException
            If there is an issue getting the user groups.
        """
        url = "{}/rest/security/usergroup/".format(self.service_url)
        if service is None:
            url += "groups/"
        else:
            url += "service/{}/groups/".format(service)

        r = self._requests("get", url)

        if r.status_code == 200:
            return parse(r.content)
        else:
            raise GeoserverException(r.status_code, r.content)

    def create_usergroup(self, group: str, service=None) -> str:
        """
        Add a new usergroup to the provided user/group service.

        Parameters
        ----------
        group : str
            The name of the user group.
        service : str, optional
            The user/group service to add the user group to.

        Returns
        -------
        str
            A success message indicating that the user group was created.

        Raises
        ------
        GeoserverException
            If there is an issue creating the user group.
        """
        url = "{}/rest/security/usergroup/".format(self.service_url)
        if service is None:
            url += "group/{}".format(group)
        else:
            url += "service/{}/group/{}".format(service, group)
        r = self._requests("post", url)

        if r.status_code == 201:
            return "Group created successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

    def delete_usergroup(self, group: str, service=None) -> str:
        """
        Deletes given usergroup from provided user/group service.

        Parameters
        ----------
        group : str
            The name of the user group to delete.
        service : str, optional
            The user/group service to delete the user group from.

        Returns
        -------
        str
            A success message indicating that the user group was deleted.

        Raises
        ------
        GeoserverException
            If there is an issue deleting the user group.
        """
        url = "{}/rest/security/usergroup/".format(self.service_url)
        if service is None:
            url += "group/{}".format(group)
        else:
            url += "service/{}/group/{}".format(service, group)

        r = self._requests("delete", url)

        if r.status_code == 200:
            return "Group deleted successfully"
        else:
            raise GeoserverException(r.status_code, r.content)

    # _______________________________________________________________________________________________
    #
    #      SERVICES
    # _______________________________________________________________________________________________
    #

    def update_service(self, service: str, **kwargs):
        """
        Update selected service's options.

        Parameters
        ----------
        service : str
            Type of service (e.g., wms, wfs)
        kwargs : dict
            Options to be modified (e.g., maxRenderingTime=600)

        Returns
        -------
        str
            A success message indicating that the options were updated.

        Raises
        ------
        GeoserverException
            If there is an issue updating the service's options.
        """
        url = "{}/rest/services/{}/settings".format(self.service_url, service)
        headers = {"content-type": "text/xml"}

        data = ""
        for key, value in kwargs.items():
            data += "<{}><{}>{}</{}></{}>".format(
                service, key, value, key, service
            )

        r = self._requests("put", url, data=data, headers=headers)

        if r.status_code == 200:
            return "Service's option updated successfully"
        else:
            raise GeoserverException(r.status_code, r.content)
