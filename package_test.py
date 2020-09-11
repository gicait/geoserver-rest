from geo.Geoserver import Geoserver
from geo.Postgres import Db
from geo.Style import catagorize_xml, classified_xml

'''
Connection
'''
geo = Geoserver('http://localhost:8080/geoserver', username='admin', password='geoserver')
# pg = Db(dbname='postgres', user='postgres', password='admin', host='localhost')
# geo.create_workspace('demo')

'''
Coverage (raster)
'''
# geo.create_coveragestore(r'C:\Users\tek\Desktop\geoserver-rest\data\C_EAR\a_Agriculture\agri_final_proj.tif', workspace='demo', overwrite=False)
# geo.upload_style(r'C:\Users\tek\Desktop\geoserver-rest\data\style\dem.sld', workspace='demo', overwrite=True)
# geo.publish_style('agri_final_proj', 'dem', 'demo')
# geo.create_coveragestyle(style_name='agri2', raster_path=r'C:\Users\tek\Desktop\geoserver-rest\data\C_EAR\a_Agriculture\agri_final_proj.tif', workspace='demo', color_ramp='terrain_r', cmap_type='values')


'''
Features (vector)
'''
# geo.create_featurestore(store_name='fdemo', workspace='demo')
# geo.publish_featurestore('fdemo','zones','demo')
# a = geo.get_featuretypes(workspace='demo', store_name='fdemo')
# a= geo.get_feature_attribute(feature_type_name='jamoat-db', workspace='demo', store_name='fdemo')
# a= geo.get_featurestore('fdemo', 'demo')
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
# geo.delete_featurestore(featurestore_name='fdemo', workspace='demo')
# geo.delete_coveragestore(coveragestore_name='agri_final_proj', workspace='demo')
# geo.delete_style(style_name='kamal2', workspace='demo')


'''
others
'''
# classified_xml('test', 'kamal', [4,5,3,12], color_ramp='hot')