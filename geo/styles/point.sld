   <FeatureTypeStyle>
     <Rule>
       <PointSymbolizer>
         <Graphic>
           <Mark>
             <WellKnownName>circle</WellKnownName>
             <Fill>
               <CssParameter name="fill">#FF0000</CssParameter>
             </Fill>
           </Mark>
           <Size>6</Size>
         </Graphic>
       </PointSymbolizer>
     </Rule>
   </FeatureTypeStyle>


<FeatureTypeStyle>
    <Rule>
    <Name>SmallPop</Name>
    <Title>1 to 50000</Title>
    <ogc:Filter>
        <ogc:PropertyIsLessThan>
        <ogc:PropertyName>pop</ogc:PropertyName>
        <ogc:Literal>50000</ogc:Literal>
        </ogc:PropertyIsLessThan>
    </ogc:Filter>
    <PointSymbolizer>
        <Graphic>
        <Mark>
            <WellKnownName>circle</WellKnownName>
            <Fill>
            <CssParameter name="fill">#0033CC</CssParameter>
            </Fill>
        </Mark>
        <Size>8</Size>
        </Graphic>
    </PointSymbolizer>
    </Rule>
    <Rule>
    <Name>MediumPop</Name>
    <Title>50000 to 100000</Title>
    <ogc:Filter>
        <ogc:And>
        <ogc:PropertyIsGreaterThanOrEqualTo>
            <ogc:PropertyName>pop</ogc:PropertyName>
            <ogc:Literal>50000</ogc:Literal>
        </ogc:PropertyIsGreaterThanOrEqualTo>
        <ogc:PropertyIsLessThan>
            <ogc:PropertyName>pop</ogc:PropertyName>
            <ogc:Literal>100000</ogc:Literal>
        </ogc:PropertyIsLessThan>
        </ogc:And>
    </ogc:Filter>
    <PointSymbolizer>
        <Graphic>
        <Mark>
            <WellKnownName>circle</WellKnownName>
            <Fill>
            <CssParameter name="fill">#0033CC</CssParameter>
            </Fill>
        </Mark>
        <Size>12</Size>
        </Graphic>
    </PointSymbolizer>
    </Rule>
    <Rule>
    <Name>LargePop</Name>
    <Title>Greater than 100000</Title>
    <ogc:Filter>
        <ogc:PropertyIsGreaterThanOrEqualTo>
        <ogc:PropertyName>pop</ogc:PropertyName>
        <ogc:Literal>100000</ogc:Literal>
        </ogc:PropertyIsGreaterThanOrEqualTo>
    </ogc:Filter>
    <PointSymbolizer>
        <Graphic>
        <Mark>
            <WellKnownName>circle</WellKnownName>
            <Fill>
            <CssParameter name="fill">#0033CC</CssParameter>
            </Fill>
        </Mark>
        <Size>16</Size>
        </Graphic>
    </PointSymbolizer>
    </Rule>
</FeatureTypeStyle>