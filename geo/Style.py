import  pycurl
import os
import seaborn as sns
from matplotlib.colors import rgb2hex

def coverage_style_xml(cmap_type, ncolor=7, min=0):
    palette = sns.color_palette('RdYlGn', int(ncolor))
    palette_hex = [rgb2hex(i) for i in palette]
    style_append = ''
    cmap_type = 'values'
    for i, color in enumerate(palette_hex):
        style_append += '<sld:ColorMapEntry color="{}" label="{}" quantity="{}"/>'.format(
            color, min+i, min+i)
    style = """
    <StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" version="1.0.0" xmlns:ogc="http://www.opengis.net/ogc" xmlns:sld="http://www.opengis.net/sld">
    <UserLayer>
        <sld:LayerFeatureConstraints>
        <sld:FeatureTypeConstraint/>
        </sld:LayerFeatureConstraints>
        <sld:UserStyle>
        <sld:Name>agri_final_proj</sld:Name>
        <sld:FeatureTypeStyle>
            <sld:Rule>
            <sld:RasterSymbolizer>
                <sld:ChannelSelection>
                <sld:GrayChannel>
                    <sld:SourceChannelName>1</sld:SourceChannelName>
                </sld:GrayChannel>
                </sld:ChannelSelection>
                <sld:ColorMap type="{}">
                    {}
                </sld:ColorMap>
            </sld:RasterSymbolizer>
            </sld:Rule>
        </sld:FeatureTypeStyle>
        </sld:UserStyle>
    </UserLayer>
    </StyledLayerDescriptor>
    """.format(cmap_type, style_append)

    with open('style.sld', 'w') as f:
        f.write(style)


def outline_only_xml(color, geom_type='polygon'):
    if geom_type=='point':
        symbolizer = '''
            <PointSymbolizer>
                <Graphic>
                <Mark>
                    <WellKnownName>circle</WellKnownName>
                    <Fill>
                    <CssParameter name="fill">{0}</CssParameter>
                    </Fill>
                </Mark>
                <Size>6</Size>
                </Graphic>
            </PointSymbolizer>
        '''.format(color)

    elif geom_type=='line':
        symbolizer = '''
                <LineSymbolizer>
                    <Stroke>
                    <CssParameter name="stroke">{0}</CssParameter>
                    <CssParameter name="stroke-width">3</CssParameter>
                    </Stroke>
                </LineSymbolizer>
            '''.format(color)

    elif geom_type=='polygon':
        symbolizer = '''
                <PolygonSymbolizer>
                    <Fill>
                        <CssParameter name="fill">#FFFFFF</CssParameter>
                    </Fill>
                    <Stroke>
                    <CssParameter name="stroke">{0}</CssParameter>
                    <CssParameter name="stroke-width">2</CssParameter>
                    </Stroke>
                </PolygonSymbolizer>
            '''.format(color)
    
    else:
        return

    style = '''
            <StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:se="http://www.opengis.net/se" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" version="1.1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <NamedLayer>
                <se:Name>Layer name</se:Name>
                <UserStyle>
                <se:Name>Layer name</se:Name>
                <se:FeatureTypeStyle>
                    <se:Rule>
                    <se:Name>Single symbol</se:Name>
                    {}
                    </se:Rule>
                </se:FeatureTypeStyle>
                </UserStyle>
            </NamedLayer>
            </StyledLayerDescriptor>
            '''.format(symbolizer)


    with open('style.sld', 'w') as f:
        f.write(style)

            

def feature_style_xml():
    pass