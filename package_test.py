from geo.Geoserver import Geoserver
from geo.Postgres import Db
from geo.Style import catagorize_xml, classified_xml

'''
Connection
'''
geo = Geoserver('http://localhost:8080/geoserver',
                username='admin', password='geoserver')
# pg = Db(dbname='postgres', user='postgres', password='admin', host='localhost')
# geo.create_workspace('demo2')

'''
New get requests
'''
# geo.get_version()
# geo.get_manifest()
# geo.get_status()
# geo.get_system_status()
# a = geo.create_shp_datastore(
#     r"C:\Program Files (x86)\GeoServer 2.15.1\data_dir\data\demo\C_Jamoat\C_Jamoat.zip", store_name='111')
# print(a)
# geo.get_layer('jamoat-db', workspace='demo')
# geo.get_datastore('111', 'demo')
# geo.get_style('hazard_exp', workspace='geoinformatics_center', )
# a = geo.get_styles()
a = geo.create_datastore(
    'datastore4', r"http://localhost:8080/geoserver/wfs?request=GetCapabilities", workspace='demo', overwrite=True)
# a = geo.create_shp_datastore('aaa', 'default')
print(a)
# geo.publish_featurestore('datastore2', 'admin_units', workspace='demo')

'''
Coverage (raster)
'''
# geo.create_coveragestore(r'C:\Users\tek\Desktop\geoserver-rest\data\C_EAR\a_Agriculture\agri_final_proj.tif', workspace='demo', overwrite=False)
#geo.upload_style(r'C:\Users\tek\Desktop\try_sld.sld', sld_version='1.1.0', workspace='try')
# geo.publish_style('agri_final_proj', 'dem', 'demo')
# color_ramp1 = {
#     'value1': '#ffff55',
#     'value2': '#505050',
#     'value3': '#404040'
# }
# geo.create_coveragestyle(style_name='demo',
#                          raster_path=r'C:\Users\tek\Desktop\try\geoserver-rest\data\flood_alert.tif',
#                          workspace='demo', color_ramp=color_ramp1, cmap_type='values', overwrite=True)


'''
Features (vector)
'''
# geo.create_featurestore(store_name='fdemo', workspace='demo')
# geo.publish_featurestore('fdemo','zones','demo')
# a = geo.get_featuretypes(workspace='demo', store_name='fdemo')
# a= geo.get_feature_attribute(feature_type_name='jamoat-db', workspace='demo', store_name='fdemo')
# a= geo.get_featurestore('fdemo', 'demo')
# store_name = 'geoinformatics_center'
# name = 'sql_view_test'
# sql = 'select id, geom, "BU" from geoinformatics_center.exp_ear'
# keyColumn = 'BU'
# workspace = 'geoinformatics_center'
# geo.delete_layer(name, workspace=workspace)
# a = geo.publish_featurestore_sqlview(
#     store_name, name, sql, key_column=keyColumn, geom_name='geom', geom_type='Geometry', workspace='geoinformatics_center')
# print(a)

"""
Feature styles
"""
# geo.create_outline_featurestyle('demo', geom_type='polygon', workspace='demo', overwrite=True)
# catagorize_xml('kamal', [1,2,3,4,5,6,7], num_of_class=30, geom_type='line')
# geo.create_catagorized_featurestyle('kamal2', [1,2,3,4,5,6,7], workspace='demo')

'''
Postgres
'''
# print(pg.get_columns_names('zones'))
# print(pg.get_all_values('zones', 'shape_area'))
# pg.create_schema('kamal kshetri')
# a = pg.get_columns_names('jamoat-db')
# print(a)
# a = pg.get_all_values('jamoat-db', 'shape_area')[5]
# print(a)

'''
Delete request
'''
# geo.delete_workspace(workspace='demo')
# geo.delete_layer(layer_name='agri_final_proj', workspace='demo')
# geo.delete_featurestore(featurestore_name='feature_store', workspace='demo')
# geo.delete_coveragestore(coveragestore_name='store_name', workspace='demo')
# geo.delete_style(style_name='kamal2', workspace='demo')


'''
others
'''
# classified_xml('test', 'kamal', [4,5,3,12], color_ramp='hot')
