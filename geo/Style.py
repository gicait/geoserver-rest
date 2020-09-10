import  pycurl
import os
import seaborn as sns
from matplotlib.colors import rgb2hex

def coverage_style_xml(color_ramp, style_name, cmap_type,  min=0, ncolor=5):
    palette = sns.color_palette(color_ramp, int(ncolor))
    palette_hex = [rgb2hex(i) for i in palette]
    style_append = ''
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
        <sld:Name>{2}</sld:Name>
        <sld:FeatureTypeStyle>
            <sld:Rule>
            <sld:RasterSymbolizer>
                <sld:ChannelSelection>
                <sld:GrayChannel>
                    <sld:SourceChannelName>1</sld:SourceChannelName>
                </sld:GrayChannel>
                </sld:ChannelSelection>
                <sld:ColorMap type="{0}">
                    {1}
                </sld:ColorMap>
            </sld:RasterSymbolizer>
            </sld:Rule>
        </sld:FeatureTypeStyle>
        </sld:UserStyle>
    </UserLayer>
    </StyledLayerDescriptor>
    """.format(cmap_type, style_append, style_name)

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
                <Size>8</Size>
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
                    <CssParameter name="stroke-width">0.26</CssParameter>
                    </Stroke>
                </PolygonSymbolizer>
            '''.format(color)
    
    else:
        print('Error: Invalid geometry type')
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

            

def catagorize_xml(column_name, values, color_ramp, geom_type='polygon'):
    N = len(values)
    palette = sns.color_palette(color_ramp, int(N))
    palette_hex = [rgb2hex(i) for i in palette]
    rule = ''
    for value, color in zip(values, palette_hex):
        if geom_type=='point':
            rule +='''
                <Rule>
                <Name>{0}</Name>
                <Title>{1}</Title>
                <ogc:Filter>
                    <ogc:PropertyIsEqualTo>
                    <ogc:PropertyName>{0}</ogc:PropertyName>
                    <ogc:Literal>{1}</ogc:Literal>
                    </ogc:PropertyIsEqualTo>
                </ogc:Filter>
                <PointSymbolizer>
                    <Graphic>
                    <Mark>
                        <WellKnownName>circle</WellKnownName>
                        <Fill>
                        <CssParameter name="fill">{2}</CssParameter>
                        </Fill>
                    </Mark>
                    <Size>5</Size>
                    </Graphic>
                </PointSymbolizer>
                </Rule>
            '''.format(column_name, value, color)
        
        elif geom_type=='line':
            rule += '''
                <Rule>
                    <Name>{1}</Name>
                    <ogc:Filter>
                        <ogc:PropertyIsEqualTo>
                        <ogc:PropertyName>{0}</ogc:PropertyName>
                        <ogc:Literal>{1}</ogc:Literal>
                        </ogc:PropertyIsEqualTo>
                    </ogc:Filter>
                    <LineSymbolizer>
                        <Stroke>
                        <CssParameter name="stroke">{2}</CssParameter>
                        <CssParameter name="stroke-width">1</CssParameter>
                        </Stroke>
                    </LineSymbolizer>
                </Rule>
            '''.format(column_name, value, color)

        elif geom_type=='polygon':
            rule += '''
                <Rule>
                    <Name>{0}</Name>
                    <Title>{1}</Title>
                    <ogc:Filter>
                        <ogc:PropertyIsEqualTo>
                        <ogc:PropertyName>{0}</ogc:PropertyName>
                        <ogc:Literal>{1}</ogc:Literal>
                        </ogc:PropertyIsEqualTo>
                    </ogc:Filter>
                    <PolygonSymbolizer>
                        <Fill>
                            <CssParameter name="fill">{2}</CssParameter>
                        </Fill>
                        <Stroke>
                            <CssParameter name="stroke">{3}</CssParameter>
                            <CssParameter name="stroke-width">0.5</CssParameter>
                        </Stroke>
                    </PolygonSymbolizer>
                </Rule>

            '''.format(column_name, value, color, '#000000')

        else:
            print('Error: Invalid geometry type')
            return

    style = '''
            <StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:se="http://www.opengis.net/se" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" version="1.1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                    <NamedLayer>
                        <se:Name>Layer name</se:Name>
                        <UserStyle>
                        <se:Name>Layer name</se:Name>
                        <FeatureTypeStyle>
                            {}
                        </FeatureTypeStyle>
                        </UserStyle>
                    </NamedLayer>
                </StyledLayerDescriptor>
        '''.format(rule)

    with open('style.sld', 'w') as f:
        f.write(style)



def classified_xml(style_name, column_name, values, color_ramp, geom_type='polygon'):
    N = len(values)
    palette = sns.color_palette(color_ramp, int(N))
    palette_hex = [rgb2hex(i) for i in palette]
    rule = ''
    for i, value, color in zip(values, palette_hex):

        print(i)

        # greater = '''
        #         <ogc:PropertyIsGreaterThan>
        #                 <ogc:PropertyName>{0}</ogc:PropertyName>
        #                 <ogc:Literal>36089389.88710001111030579</ogc:Literal>
        #             </ogc:PropertyIsGreaterThan>
        #         '''

        # less = '''
        #         <ogc:PropertyIsLessThanOrEqualTo>
        #                 <ogc:PropertyName>{0}</ogc:PropertyName>
        #                 <ogc:Literal>76042934.05079999566078186</ogc:Literal>
        #             </ogc:PropertyIsLessThanOrEqualTo>
        #         '''


        rule += '''
            <se:Rule>
                <se:Name>{1}</se:Name>
                <se:Description>
                    <se:Title>{1}</se:Title>
                </se:Description>
                <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
                    <ogc:And>
                    <ogc:PropertyIsGreaterThan>
                        <ogc:PropertyName>{0}</ogc:PropertyName>
                        <ogc:Literal>36089389.88710001111030579</ogc:Literal>
                    </ogc:PropertyIsGreaterThan>
                    <ogc:PropertyIsLessThanOrEqualTo>
                        <ogc:PropertyName>{0}</ogc:PropertyName>
                        <ogc:Literal>76042934.05079999566078186</ogc:Literal>
                    </ogc:PropertyIsLessThanOrEqualTo>
                    </ogc:And>
                </ogc:Filter>
                <se:PolygonSymbolizer>
                    <se:Fill>
                    <se:SvgParameter name="fill">{2}</se:SvgParameter>
                    </se:Fill>
                    <se:Stroke>
                    <se:SvgParameter name="stroke">{3}</se:SvgParameter>
                    <se:SvgParameter name="stroke-width">1</se:SvgParameter>
                    <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
                    </se:Stroke>
                </se:PolygonSymbolizer>
            </se:Rule>

        '''.format(column_name, value, color, '#000000')

    style = '''
            <StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:se="http://www.opengis.net/se" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" version="1.1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                    <NamedLayer>
                        <se:Name>Layer name</se:Name>
                        <UserStyle>
                        <se:Name>Layer name</se:Name>
                        <FeatureTypeStyle>
                            {}
                        </FeatureTypeStyle>
                        </UserStyle>
                    </NamedLayer>
                </StyledLayerDescriptor>
        '''.format(rule)

    with open('style.sld', 'w') as f:
        f.write(style)
