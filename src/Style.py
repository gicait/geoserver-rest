import  pycurl
import os
import seaborn as sns
from matplotlib.colors import rgb2hex

def coverage_style_xml(cmap_type, ncolor=7, min=0, max=9):
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

    