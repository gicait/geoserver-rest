from src.Geoserver import Geoserver

geo = Geoserver()
# geo.create_workspace('try')
# geo.create_coveragestore(r'C:\Users\tek\Desktop\geoserver-rest\data\C_EAR\a_Agriculture\agri_final_proj.tif', workspace='try')
# geo.create_featurestore('try_feature', 'try', 'tajikistan', '203.159.29.40', pg_password='Pxfd#f%Ar')
# geo.publish_featurestore('try', 'try_feature', 'country')
# geo.apply_style('country', 'polygon', 'try')

geo.create_coveragestyle('try3', 'try')