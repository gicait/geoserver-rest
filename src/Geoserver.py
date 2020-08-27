import  pycurl
import os
import io
from .Style import coverage_style_xml

#call back class for read the data
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


    def create_workspace(self, workspace):
        """
        Create a new workspace in geoserver, geoserver workspace url will be same as name of the workspace
        """
        try:
            c=pycurl.Curl()
            workspace_xml="<workspace><name>{0}</name></workspace>".format(workspace)
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password) 
            c.setopt(c.URL, '{0}/rest/workspaces'.format(self.service_url))
            c.setopt(pycurl.HTTPHEADER, ["Content-type: text/xml"])
            c.setopt(pycurl.POSTFIELDSIZE, len(workspace_xml))
            c.setopt(pycurl.READFUNCTION,DataProvider(workspace_xml).read_cb)
            c.setopt(pycurl.POST, 1)
            c.perform()
            c.close()
        except Exception as e:
            return 'Error: {}'.format(e)


    def create_coveragestore(self, path, workspace, lyr_name=None, file_type='GeoTIFF', content_type='image/tiff', overwrite=False):
        """
        created the coveragestore, data will uploaded to the server
        the name parameter will be the name of coveragestore (coveragestore name will be assigned as the file name incase of not providing name parameter) 
        the path to the file and file_type indicating it is a geotiff, arcgrid or other raster type
        """

        # overwrite feature needs to be write again
        try:
            file_size =os.path.getsize(path)

            c=pycurl.Curl()

            if lyr_name:
                file_name = lyr_name

            else:
                file_name = os.path.basename(path)
                f=file_name.split(".")
                if len(f)>0:
                    file_name=f[0]  

            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)    
            file_type=file_type.lower()
            c.setopt(c.URL, '{0}/rest/workspaces/{1}/coveragestores/{2}/file.{3}'.format(self.service_url,workspace,file_name,file_type))
            c.setopt(pycurl.HTTPHEADER, ["Content-type:{}".format(content_type) ])
            c.setopt(pycurl.READFUNCTION,FileReader(open(path, 'rb')).read_callback)
            c.setopt(pycurl.INFILESIZE,file_size)
            c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()
            c.close()
        except Exception as e:
            return 'Error: {}'.format(e)
        
        
    def create_featurestore(self, store, workspace, db, host='localhost', port=5432, schema='public', pg_user='postgres', pg_password='admin'):
        """
        Postgis store for connecting postgres with geoserver
        After creating feature store, you need to publish it
        Input parameters:specify the store name you want to be created, the postgis database parameters including host, port, database name, schema, user and password, 
        """
        try:
            c = pycurl.Curl()
            #connect with geoserver
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password) 
            c.setopt(c.URL, '{0}/rest/workspaces/{1}/datastores'.format(self.service_url, workspace))
            c.setopt(pycurl.HTTPHEADER, ["Content-type: text/xml"])
        
            #make the connection with postgis database  
            database_connection='<dataStore>'\
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
            '</dataStore>'.format(store,host,port,db,schema,pg_user,pg_password)
            c.setopt(pycurl.POSTFIELDSIZE, len(database_connection))
            c.setopt(pycurl.READFUNCTION,DataProvider(database_connection).read_cb)
            c.setopt(pycurl.POST, 1)
            c.perform()
            c.close()
        except Exception as e:
            return "Error:%s"%str(e)


    def publish_featurestore(self, workspace, store, pg_table):
        """
        Only user for postgis vector data
        input parameters: specify the name of the table in the postgis database to be published, specify the store,workspace name, and  the Geoserver user name, password and URL
        """
        try:
            c = pycurl.Curl()
            layer_xml="<featureType><name>{0}</name></featureType>".format(pg_table)
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)
            #connecting with the specified store in geoserver
            c.setopt(c.URL, '{0}/rest/workspaces/{1}/datastores/{2}/featuretypes'.format(self.service_url, workspace, store))
            c.setopt(pycurl.HTTPHEADER, ["Content-type: text/xml"])
            c.setopt(pycurl.POSTFIELDSIZE, len(layer_xml))
            c.setopt(pycurl.READFUNCTION,DataProvider(layer_xml).read_cb)
            c.setopt(pycurl.POST, 1)
            c.perform()
            c.close()
        
        except Exception as e:
            return "Error:%s"%str(e)


    def apply_style(self, layer_name, style_name,workspace, content_type='text/xml'):
        """
        publishing a raster file to geoserver
        the coverage store will be created automatically as the same name as the raster layer name. 
        input parameters: the parameters connecting geoserver (user,password, url and workspace name),the path to the file and file_type indicating it is a geotiff, arcgrid or other raster type
        """

        try:
            c = pycurl.Curl()
            style_xml="<layer><defaultStyle><name>{0}</name></defaultStyle></layer>".format(style_name)
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)
            c.setopt(c.URL, '{0}/rest/layers/{1}:{2}'.format(self.service_url, workspace, layer_name))
            c.setopt(pycurl.HTTPHEADER, ["Content-type: {}".format(content_type)])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION,DataProvider(style_xml).read_cb)
            #c.setopt(pycurl.CUSTOMREQUEST, "PUT")
            c.setopt(pycurl.PUT, 1)
            c.perform()
            c.close()
        except Exception as e:
            return 'Error: {}'.format(e)

    def create_coveragestyle(self, name, workspace, cmap_type='values', ncolors=7):
        '''
        This function will dynamically create the style file for raster. 
        Inputs: name of file, workspace, cmap_type (two options: values, range), ncolors: determins the number of class, min for minimum value of the raster, max for the max value of raster
        '''
        try:
            coverage_style_xml(cmap_type, ncolors)
            style_xml = "<style><name>{0}</name><filename>{1}</filename></style>".format(name,name+'.sld')

            # create the xml file for associated style 
            c = pycurl.Curl()
            c.setopt(pycurl.USERPWD, self.username + ':' + self.password)
            c.setopt(c.URL, '{0}/rest/workspaces/{1}/styles'.format(self.service_url, workspace))
            c.setopt(pycurl.HTTPHEADER, ['Content-type:text/xml'])
            c.setopt(pycurl.POSTFIELDSIZE, len(style_xml))
            c.setopt(pycurl.READFUNCTION, DataProvider(style_xml).read_cb)
            c.setopt(pycurl.POST, 1)
            c.perform()

            # upload the style file
            c.setopt(c.URL, '{0}/rest/workspaces/{1}/styles/{2}'.format(self.service_url, workspace, name))
            c.setopt(pycurl.HTTPHEADER, ["Content-type:application/vnd.ogc.sld+xml" ])
            c.setopt(pycurl.READFUNCTION,FileReader(open('style.sld', 'rb')).read_callback)
            c.setopt(pycurl.INFILESIZE,os.path.getsize('style.sld'))
            c.setopt(pycurl.POST, 1)
            c.setopt(pycurl.UPLOAD, 1)
            c.perform()
            c.close()

            # remove temporary style created style file 
            os.remove('style.sld')

        except Exception as e:
            return 'Error: {}'.format(e)