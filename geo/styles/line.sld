   <FeatureTypeStyle>
     <Rule>
       <LineSymbolizer>
         <Stroke>
           <CssParameter name="stroke">#000000</CssParameter>
           <CssParameter name="stroke-width">3</CssParameter>
         </Stroke>
       </LineSymbolizer>
     </Rule>
   </FeatureTypeStyle>




<FeatureTypeStyle>
    <Rule>
    <Name>local-road</Name>
    <ogc:Filter>
        <ogc:PropertyIsEqualTo>
        <ogc:PropertyName>type</ogc:PropertyName>
        <ogc:Literal>local-road</ogc:Literal>
        </ogc:PropertyIsEqualTo>
    </ogc:Filter>
    <LineSymbolizer>
        <Stroke>
        <CssParameter name="stroke">#009933</CssParameter>
        <CssParameter name="stroke-width">2</CssParameter>
        </Stroke>
    </LineSymbolizer>
    </Rule>
</FeatureTypeStyle>
<FeatureTypeStyle>
    <Rule>
    <Name>secondary</Name>
    <ogc:Filter>
        <ogc:PropertyIsEqualTo>
        <ogc:PropertyName>type</ogc:PropertyName>
        <ogc:Literal>secondary</ogc:Literal>
        </ogc:PropertyIsEqualTo>
    </ogc:Filter>
    <LineSymbolizer>
        <Stroke>
        <CssParameter name="stroke">#0055CC</CssParameter>
        <CssParameter name="stroke-width">3</CssParameter>
        </Stroke>
    </LineSymbolizer>
    </Rule>
</FeatureTypeStyle>
<FeatureTypeStyle>
    <Rule>
    <Name>highway</Name>
    <ogc:Filter>
        <ogc:PropertyIsEqualTo>
        <ogc:PropertyName>type</ogc:PropertyName>
        <ogc:Literal>highway</ogc:Literal>
        </ogc:PropertyIsEqualTo>
    </ogc:Filter>
    <LineSymbolizer>
        <Stroke>
        <CssParameter name="stroke">#FF0000</CssParameter>
        <CssParameter name="stroke-width">6</CssParameter>
        </Stroke>
    </LineSymbolizer>
    </Rule>
</FeatureTypeStyle>
