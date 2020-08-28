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


def outline_only_xml(hex_code='#3579b1'):
    style = '''
            <StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:se="http://www.opengis.net/se" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" version="1.1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <NamedLayer>
                <se:Name>Country_region</se:Name>
                <UserStyle>
                <se:Name>Country_region</se:Name>
                <se:FeatureTypeStyle>
                    <se:Rule>
                    <se:Name>Single symbol</se:Name>
                    <se:LineSymbolizer>
                        <se:Stroke>
                        <se:SvgParameter name="stroke">{}</se:SvgParameter>
                        <se:SvgParameter name="stroke-width">1</se:SvgParameter>
                        <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
                        <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
                        </se:Stroke>
                    </se:LineSymbolizer>
                    </se:Rule>
                </se:FeatureTypeStyle>
                </UserStyle>
            </NamedLayer>
            </StyledLayerDescriptor>
            '''.format(hex_code)

    with open('style.sld', 'w') as f:
        f.write(style)

            

def feature_style_xml():
    pass