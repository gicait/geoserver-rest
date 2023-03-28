import os
import unittest
from environs import Env

from unittest.mock import MagicMock, patch #allows replacing methods ans Objects by Mocks
from ddt import data, ddt, unpack #allows running the same test with different parameters

from geo.Geoserver import Geoserver

@ddt
class TestLayerGroup(unittest.TestCase):
    """
    Tests all layergroup related methods of the geoserver class.

    How to use:

    You need to have a geoserver that you can use for testing.
    In order to run the test, you need to create an .env file based on the .env_template.
    Adjust the .env file with the url and login information for the server you're testing against.

    You can run this test by executing:
    python -m unittest tests.test_layergroup

    The test will temporarily create a new workspace "unittest" on your geoserver. This workspace
    (or any workspace of that name that previously existed on your geoserver) will be deleted
    after the test.

    The setup of this test relies on the create_workspace, delete_workspace, 
    and create_coveragestore methods.

    """

    @classmethod
    def setUpClass(cls):
        '''
        is run once when setting up the test class

        sets up a geoserver instance, builds a workspace, 
        and uploads 2 example layers that we can later on use to build our layergroups
        '''

        env = Env()
        env.read_env()

        cls.geoserver = Geoserver(
            os.environ["GEOSERVER_URL"], 
            username= os.environ["GEOSERVER_USER"],
            password=os.environ["GEOSERVER_PASSWORD"]
            )

        # set up workspace for testing
        try:
            cls.geoserver.create_workspace(workspace="unittest")
        except:
            # is raised when the workspace exists already
            cls.geoserver.delete_workspace(workspace="unittest")
            cls.geoserver.create_workspace(workspace="unittest")

        # upload sample layers to the testing workspace
        # credits for the sample file: https://github.com/mommermi/geotiff_sample

        cls.geoserver.create_coveragestore(
                layer_name="test_layer_1",
                path="tests/data/sample_geotiff.tif", 
                workspace="unittest"
            )

        cls.geoserver.create_coveragestore(
                layer_name="test_layer_2",
                path="tests/data/sample_geotiff.tif", 
                workspace="unittest"
            )

        cls.geoserver.create_coveragestore(
                layer_name="test_layer_3",
                path="tests/data/sample_geotiff.tif", 
                workspace="unittest"
            )


    @classmethod
    def tearDownClass(cls):
        '''
        is run when tearing down test class
        '''
        cls.geoserver.delete_workspace(workspace="unittest")

    def setUp(self):
        '''
        is run before each individual test method
        '''
        pass
        
    def tearDown(self):
        '''
        is run after each individual test method
        '''
        # delete any remaining layergroups in the unittest workspace
        layergroups = self.geoserver.get_layergroups(workspace="unittest")

        if layergroups["layerGroups"] == '':
            pass

        else:
            for layer_group_info in layergroups["layerGroups"]["layerGroup"]:
                self.geoserver.delete_layergroup(
                    layergroup_name = layer_group_info["name"],
                    workspace="unittest"
                )

        #delete any specific testing layergroup from the global workspace
        try:
            self.geoserver.delete_layergroup("test-layergroup-name")
        except:
            pass


    @data(
        ("NonExistingLayerGroup", None), #layergroup in global workspace
        ("NonExistingLayerGroup", "unittest") #layergroup in our workspace
        )
    @unpack
    def test_get_layergroup_that_doesnt_exist(self, layergroup_name, workspace):

        with self.assertRaises(Exception):

            self.geoserver.get_layergroup(
                layer_name=layergroup_name,
                workspace=workspace
            )

    @data(
        ("NonExistingLayerGroup", None), #layergroup in global workspace
        ("NonExistingLayerGroup", "unittest") #layergroup in our workspace
        )
    @unpack
    def test_delete_layergroup_that_doesnt_exist(self, layergroup_name, workspace):

        with self.assertRaises(Exception):

            self.geoserver.delete_layergroup(
                layergroup_name=layergroup_name,
                workspace=workspace
            )

    @data(
        (
            "test-layergroup-name", #name
            "single", #mode
            "test-layergroup-title", #title
            "test-layergroup-abstract-text", #abstractText
            ["keyword_1", "keyword_2"], #keywords
            "unittest" #workspace
        ),
        (
            "test-layergroup-name", #name
            "single", #mode
            "test-layergroup-title", #title
            "test-layergroup-abstract-text", #abstractText
            ["keyword_1", "keyword_2"], #keywords
            None #workspace
        ),
        )
    @unpack
    def test_create_and_get_and_delete_layergroup(self, name, mode, title, abstract_text, keywords, workspace):

        self.geoserver.create_layergroup(
            name = name,
            mode = mode,
            title = title,
            abstract_text = abstract_text,
            layers = ["test_layer_1", "test_layer_2"],
            workspace = workspace,
            keywords = keywords
        )

        layer_group_dict = self.geoserver.get_layergroup(
            layer_name = name,
            workspace=workspace,
        )

        self.assertIsInstance(layer_group_dict, dict)

        self.assertEqual(
            layer_group_dict["layerGroup"]["name"], name
        )

        self.assertEqual(
            layer_group_dict["layerGroup"]["mode"], mode.upper()
        )

        self.assertEqual(
            layer_group_dict["layerGroup"]["title"], title
        )

        self.assertEqual(
            layer_group_dict["layerGroup"]["abstractTxt"], abstract_text
        )

        if workspace is not None:
            self.assertEqual(
                layer_group_dict["layerGroup"]["workspace"]["name"],
                workspace,
                "layer_group has not been assigned to the right workspace"
            )
        
        self.assertEqual(
            len(layer_group_dict["layerGroup"]["publishables"]["published"]),
            2,
            f'{len(layer_group_dict["layerGroup"]["publishables"]["published"])} instead of 2 layers in layergroup'
        )

        self.assertEqual(
            layer_group_dict["layerGroup"]["keywords"]["string"],
            keywords
        )

        self.geoserver.delete_layergroup(
            layergroup_name=name,
            workspace=workspace
        )

        with self.assertRaises(Exception) as assertion:
            assertion.msg = "Layer group has not been deleted properly."
            self.geoserver.get_layergroup(
            layer_name = name,
            workspace=workspace,
        )

    @data("unittest", None)
    def test_add_layer_to_layergroup(self, workspace):

        self.geoserver.create_layergroup(
            name = "test-layergroup-name",
            mode = "single",
            title = "test_layergroup_to_add",
            abstract_text = "this is an abstract text",
            layers = ["test_layer_1"],
            workspace = workspace,
            keywords = []
        )

        layer_group_dict = self.geoserver.get_layergroup(
            layer_name = "test-layergroup-name",
            workspace=workspace,
        )
        
        self.assertIsInstance(
            layer_group_dict["layerGroup"]["publishables"]["published"],
            dict,
            f'presumably more than 1 layer in layergroup (layer_group_dict["layerGroup"]["publishables"]["published"] is list instead of dict)'
        )

        self.geoserver.add_layer_to_layergroup(
            layergroup_name = "test-layergroup-name",
            layergroup_workspace = workspace,
            layer_name = "test_layer_2",
            layer_workspace = "unittest"
        )

        updated_layer_group_dict = self.geoserver.get_layergroup(
            layer_name = "test-layergroup-name",
            workspace=workspace,
        )
        
        self.assertEqual(
            len(updated_layer_group_dict["layerGroup"]["publishables"]["published"]),
            2,
            f'{len(updated_layer_group_dict["layerGroup"]["publishables"]["published"])} instead of 2 layers in layergroup'
        )

        self.geoserver.add_layer_to_layergroup(
            layergroup_name = "test-layergroup-name",
            layergroup_workspace = workspace,
            layer_name = "test_layer_3",
            layer_workspace = "unittest"
        )

        updated_layer_group_dict = self.geoserver.get_layergroup(
            layer_name = "test-layergroup-name",
            workspace=workspace,
        )
        
        self.assertEqual(
            len(updated_layer_group_dict["layerGroup"]["publishables"]["published"]),
            3,
            f'{len(updated_layer_group_dict["layerGroup"]["publishables"]["published"])} instead of 3 layers in layergroup'
        )

    def test_add_layer_to_layergroup_that_doesnt_exist(self):

        with self.assertRaises(Exception):

            self.geoserver.add_layer_to_layergroup(
                layergroup_name = "foo",
                layergroup_workspace = "unittest",
                layer_name = "test_layer_2",
                layer_workspace = "unittest"
            )

    def test_add_layer_that_doesnt_exist_to_layergroup(self):

        self.geoserver.create_layergroup(
            name = "test-layergroup-name",
            mode = "single",
            title = "test_layergroup_to_add",
            abstract_text = "this is an abstract text",
            layers = ["test_layer_1"],
            workspace = "unittest",
            keywords = []
        )

        with self.assertRaises(Exception):

            self.geoserver.add_layer_to_layergroup(
                layergroup_name = "test-layergroup-name",
                layergroup_workspace = "unittest",
                layer_name = "bar",
                layer_workspace = "unittest"
            )

    @data("unittest", None)
    def test_remove_layer_from_layergroup(self, workspace):

        self.geoserver.create_layergroup(
            name = "test-layergroup-name",
            mode = "single",
            title = "test_layergroup_to_add",
            abstract_text = "this is an abstract text",
            layers = ["test_layer_1", "test_layer_2", "test_layer_3"],
            workspace = workspace,
            keywords = []
        )

        self.geoserver.remove_layer_from_layergroup(
            layergroup_name = "test-layergroup-name",
            layergroup_workspace = workspace,
            layer_name = "test_layer_1",
            layer_workspace = "unittest"
        )

        updated_layer_group_dict = self.geoserver.get_layergroup(
            layer_name = "test-layergroup-name",
            workspace=workspace,
        )

        self.assertEqual(
            len(updated_layer_group_dict["layerGroup"]["publishables"]["published"]),
            2,
            f'{len(updated_layer_group_dict["layerGroup"]["publishables"]["published"])} instead of 2 layers in layergroup'
        )

    def test_remove_layer_from_layergroup_that_doesnt_exist(self):

        with self.assertRaises(Exception):

            self.geoserver.remove_layer_from_layergroup(
                layergroup_name = "foo",
                layergroup_workspace = "unittest",
                layer_name = "test_layer_2",
                layer_workspace = "unittest"
            )

    def test_remove_layer_that_doesnt_exist_from_layergroup(self):

        self.geoserver.create_layergroup(
            name = "test-layergroup-name",
            mode = "single",
            title = "test_layergroup_to_add",
            abstract_text = "this is an abstract text",
            layers = ["test_layer_1"],
            workspace = "unittest",
            keywords = []
        )

        with self.assertRaises(Exception):

            self.geoserver.remove_layer_from_layergroup(
                layergroup_name = "test-layergroup-name",
                layergroup_workspace = "unittest",
                layer_name = "bar",
                layer_workspace = "unittest"
            )

if __name__ == '__main__':
    unittest.main()
