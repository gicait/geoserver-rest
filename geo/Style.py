# inbuilt libraries
from typing import Dict, Iterable, List, Union

# third-party libraries
import seaborn as sns
from matplotlib.colors import rgb2hex


def coverage_style_colormapentry(
    color_ramp: Union[List, Dict, Iterable],
    min_value: float,
    max_value: float,
    number_of_classes: int = None,
):
    """

    Parameters
    ----------
    color_ramp
    min_value
    max_value
    number_of_classes

    Returns
    -------

    Notes
    -----
    This is the core function for controlling the layers styles
    The color_ramp can be list or dict or touple or str
    min, max will be dynamically calculated value from raster
    number_of_classes will be available in map legend
    """
    style_append = ""
    n = len(color_ramp)

    if isinstance(color_ramp, list):

        if n != number_of_classes:
            number_of_classes = n

        interval = (max_value - min_value) / (number_of_classes - 1)

        for i, color in enumerate(color_ramp):
            value = min_value + interval * i
            value = round(value, 1)

            style_append += (
                '<sld:ColorMapEntry color="{}" label="{}" quantity="{}"/>'.format(
                    color, value, value
                )
            )

    elif isinstance(color_ramp, dict):

        if n != number_of_classes:
            number_of_classes = n

        interval = (max_value - min_value) / (number_of_classes - 1)

        for name, color, i in zip(color_ramp.keys(), color_ramp.values(), range(n)):
            value = min_value + interval * i

            style_append += (
                '<sld:ColorMapEntry color="{}" label=" {}" quantity="{}"/>'.format(
                    color, name, value
                )
            )

    else:
        for i, color in enumerate(color_ramp):
            interval = (max_value - min_value) / (number_of_classes - 1)
            value = min_value + interval * i

            style_append += (
                '<sld:ColorMapEntry color="{}" label="{}" quantity="{}"/>'.format(
                    color, value, value
                )
            )

    return style_append


def coverage_style_xml(
    color_ramp, style_name, cmap_type, min_value, max_value, number_of_classes
):
    min_max_difference = max_value - min_value
    style_append = ""
    interval = min_max_difference / (number_of_classes - 1)  # noqa

    # The main style of the coverage style
    if isinstance(color_ramp, str):
        palette = sns.color_palette(color_ramp, int(number_of_classes))
        color_ramp = [rgb2hex(i) for i in palette]

    style_append += coverage_style_colormapentry(
        color_ramp, min_value, max_value, number_of_classes
    )

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
    """.format(
        cmap_type, style_append, style_name
    )

    with open("style.sld", "w") as f:
        f.write(style)


def outline_only_xml(color, geom_type="polygon"):
    if geom_type == "point":
        symbolizer = """
            <PointSymbolizer>
                <Graphic>
                <Mark>
                    <WellKnownName>circle</WellKnownName>
                    <Fill>
                    <CssParameter name="fill">{}</CssParameter>
                    </Fill>
                </Mark>
                <Size>8</Size>
                </Graphic>
            </PointSymbolizer>
        """.format(
            color
        )

    elif geom_type == "line":
        symbolizer = """
                <LineSymbolizer>
                    <Stroke>
                    <CssParameter name="stroke">{}</CssParameter>
                    <CssParameter name="stroke-width">3</CssParameter>
                    </Stroke>
                </LineSymbolizer>
            """.format(
            color
        )

    elif geom_type == "polygon":
        symbolizer = """
                <PolygonSymbolizer>
                    <Fill>
                        <CssParameter name="fill">#FFFFFF</CssParameter>
                    </Fill>
                    <Stroke>
                    <CssParameter name="stroke">{}</CssParameter>
                    <CssParameter name="stroke-width">0.26</CssParameter>
                    </Stroke>
                </PolygonSymbolizer>
            """.format(
            color
        )

    else:
        print("Error: Invalid geometry type")
        return

    style = """
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
            """.format(
        symbolizer
    )

    with open("style.sld", "w") as f:
        f.write(style)


def catagorize_xml(
    column_name: str,
    values: List[float],
    color_ramp: str = None,
    geom_type: str = "polygon",
):
    n = len(values)
    palette = sns.color_palette(color_ramp, int(n))
    palette_hex = [rgb2hex(i) for i in palette]
    rule = ""
    for value, color in zip(values, palette_hex):
        if geom_type == "point":
            rule += """
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
            """.format(
                column_name, value, color
            )

        elif geom_type == "line":
            rule += """
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
            """.format(
                column_name, value, color
            )

        elif geom_type == "polygon":
            rule += """
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

            """.format(
                column_name, value, color, "#000000"
            )

        else:
            print("Error: Invalid geometry type")
            return

    style = """
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
        """.format(
        rule
    )

    with open("style.sld", "w") as f:
        f.write(style)


def classified_xml(
    style_name: str,
    column_name: str,
    values: List[float],
    color_ramp: str = None,
    geom_type: str = "polygon",
):
    max_value = max(values)
    min_value = min(values)
    diff = max_value - min_value
    n = 5
    interval = diff / 5
    palette = sns.color_palette(color_ramp, int(n))
    palette_hex = [rgb2hex(i) for i in palette]
    # interval = N/4
    # color_values = [{value: color} for value, color in zip(values, palette_hex)]
    # print(color_values)
    rule = ""
    for i, color in enumerate(palette_hex):
        print(i)

        rule += """
            <se:Rule>
                <se:Name>{1}</se:Name>
                <se:Description>
                    <se:Title>{4}</se:Title>
                </se:Description>
                <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
                    <ogc:And>
                    <ogc:PropertyIsGreaterThan>
                        <ogc:PropertyName>{0}</ogc:PropertyName>
                        <ogc:Literal>{5}</ogc:Literal>
                    </ogc:PropertyIsGreaterThan>
                    <ogc:PropertyIsLessThanOrEqualTo>
                        <ogc:PropertyName>{0}</ogc:PropertyName>
                        <ogc:Literal>{4}</ogc:Literal>
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

        """.format(
            column_name,
            style_name,
            color,
            "#000000",
            min_value + interval * i,
            min_value + interval * (i + 1),
        )

    style = """
            <StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ogc="http://www.opengis.net/ogc" version="1.1.0" xmlns:se="http://www.opengis.net/se" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd">
                <NamedLayer>
                    <se:Name>{0}</se:Name>
                    <UserStyle>
                    <se:Name>{0}</se:Name>
                        <se:FeatureTypeStyle>
                            {1}
                        </se:FeatureTypeStyle>
                    </UserStyle>
                </NamedLayer>
            </StyledLayerDescriptor>
        """.format(
        style_name, rule
    )

    with open("style.sld", "w") as f:
        f.write(style)
