<a href="https://essays.juncture-digital.org"><img src="https://gitcdn.link/repo/jstor-labs/juncture/main/images/ve-button.png"></a>

<param ve-config
       title="Map examples"
       banner="https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/WorldMap-A_with_Frame.png/1024px-WorldMap-A_with_Frame.png"
       layout="vtl"
       author="JSTOR Labs team">

## Introduction

This sample essay provides examples showing how maps can be incorporated into an essay.  Various features are used in the examples.
The most basic map tag is `<param ve-map>`.  Inserting this tag into an essay will result in a map at the default location and zoom level using the standard base map.  The map center defaults to `25` (latitude) and `0` (longitude).  The zoom level defaults to `2.5`.  The standard base map is `OpenStreetMap`. 
<param ve-map>

```markdown
<param ve-map>
```

## Setting the base map

 By default, `OpenStreetMap` (OSM) is used for the base map. [Other base maps are available](/help#ve-map-attributes) and can be used by adding the `basemap` attribute to the `ve-map` tag.
<param ve-map basemap="Esri_WorldPhysical">

```markdown
<param ve-map basemap="Esri_WorldPhysical">
```

## A map with custom center and zoom

Maps can be customized in many ways but the most common customizations are to set a center point and zoom level.  The center point can be set using the latitude and logitude values or by specifiying the Wikidata QID for the location in which case the visual essay tool will query Wikidata for the corresponding lat/lon coordinates.  In this example, centering the map on Rome, the lat/lon coordinates are explicitly set.
<param ve-map center="41.893,12.483" zoom="10">

```markdown
<param ve-map center="41.893,12.483" zoom="10">
```

## A map with custom center using Wikidata entity for coordinates

This map should look identical to the previous one.  The difference is that we're using the Wikidata identifier (`Q2201`) for Rome as the center attribute in the map tag.  When a Wikidata identifier is use the geographic coordinates are automatically retrieved from Wikidata.
<param ve-map center="Q220" zoom="10">

```markdown
<param ve-map center="Q220" zoom="10">
```

## A map with a marker {#marker}

In this example we're again using Rome as the center point.  We've also added an entity tag for Rome (`<param ve-entity eid="Q220">`) and a mention in this paragraph text which will result in a location marker automatically added to the map.
<param ve-entity eid="Q220">
<param ve-map center="Q220" zoom="10">

```markdown
<param ve-entity eid="Q220">
<param ve-map center="Q220" zoom="10">
```

## A map with a circle marker and labels opened on map display 

The default behavior is to display location labels only when the mouse hovers over the marker.  If the `show-labels` attribute is addded to the `ve-map` tag labels will be automatically displayed when the map is opened, as is the case for Rome in the example.
<param ve-entity eid="Q220">
<param ve-map center="Q220" zoom="10" show-labels marker-type="circle" radius="8">

```markdown
<param ve-entity eid="Q220">
<param ve-map center="Q220" zoom="10" show-labels marker-type="circle" radius="8">
```

## Displaying GeoJSON shapes instead of markers {#geojson}

Many location entities in Wikidata can automatically be associated with a GeoJSON
region in addition to the latitude and longitude coordinates.  Adding the `prefer-geojson` attribute to the `ve-map` tag will result in the GeoJSON shape being
used for Rome on the map instead of a marker.
<param ve-entity eid="Q220">
<param ve-map center="Q220" zoom="10" prefer-geojson>

```markdown
<param ve-entity eid="Q220">
<param ve-map center="Q220" zoom="10" prefer-geojson>
```

## Using custom GeoJSON map layer 

One or more external GeoJSON files can be used as map layers.  Each file is specified in a separate `ve-map-layer` tag.  
The tag includes a `geojson` attribute identifying it as a GeoJson layer with a `url` attribute identifying the location of 
the GeoJSON file.  In this example markers are displayed for the 100 largest cities in the world based on population data obtained from Wikidata.
<param ve-map zoom="2">
<param ve-map-layer geojson title="Worlds most populated cities" url="cities.json">

```markdown
<param ve-map zoom="2">
<param ve-map-layer geojson title="Worlds most populated cities" url="cities.json">
```

By default, points in a GeoJSON layer are displayed as standard markers.  In some cases alternate syling may be desired, especially in
cases where may points are displayed.  In this example the same GeoJSON layer is used but the marker styling is customized in the `ve-map` tag.
<param ve-map
       zoom="2"
       marker-type="circle"
       radius="4" 
       stroke-width="0"
       fill="blue" 
       fill-opacity="1">
<param ve-map-layer geojson title="Worlds most populated cities" url="cities.json">

```markdown
<param ve-map
       zoom="2"
       marker-type="circle"
       radius="4" 
       stroke-width="0"
       fill="blue" 
       fill-opacity="1">
<param ve-map-layer geojson title="Worlds most populated cities" url="cities.json">
```

## Controlling visibility of map data using time {#time-dimension}

### Using external GeoJSON map layer with time dimension 

For GeoJSON data that is time tagged a time dimension extension is available for filtering and animatating location data based on date/time.  The time dimension control is activated by including the `time-dimension` attribute in the `ve-map` tag.  The time dimension control can configured using a number of optional attributes.  The supported attributes can be seen on the [help](/help#ve-map) page.
<param ve-map 
       zoom="2"
       time-dimension
       time-interval="-008000/"
       duration="P10000Y"
       basemap="Esri_WorldGrayCanvas"
       max-zoom="4"
       date-format="YYYY"
       auto-play="true"
       auto-fit="false"
       fps="4"
       marker-type="circle"
       radius="4" 
       stroke-width="0"
       fill="blue" 
       fill-opacity="1">
<param ve-map-layer geojson 
       title="Worlds most populated cities"
       url="cities.json">

```markdown
<param ve-map 
       zoom="2"
       time-dimension
       time-interval="-008000/"
       duration="P10000Y"
       basemap="Esri_WorldGrayCanvas"
       max-zoom="4"
       date-format="YYYY"
       auto-play="true"
       auto-fit="false"
       fps="4"
       marker-type="circle"
       radius="4" 
       stroke-width="0"
       fill="blue" 
       fill-opacity="1">
<param ve-map-layer geojson
       title="Worlds most populated cities"
       url="cities.json">
```

### US States Entry

For GeoJSON data that is time tagged a time dimension extension is available for filtering and animatating location data based on date/time.  The time dimension control is activated by including the `time-dimension` attribute in the `ve-map` tag.  The time dimension control can configured using a number of optional attributes.  The supported attributes can be seen on the [help](/help#ve-map) page.
<param ve-map 
       center="39.833333, -98.583333"
       zoom="4"
       time-dimension
       time-interval="1780/"
       duration="P500Y"
       basemap="Esri_WorldGrayCanvas"
       max-zoom="4"
       date-format="YYYY"
       fps="4">
<param ve-map-layer geojson title="US States" url="us-states.json">

```markdown
<param ve-map 
       center="39.833333, -98.583333"
       zoom="4"
       time-dimension
       time-interval="1780/"
       duration="P500Y"
       basemap="Esri_WorldGrayCanvas"
       max-zoom="4"
       date-format="YYYY"
       fps="4">
<param ve-map-layer geojson title="US States" url="us-states.json">
```

## Using a georeferenced image overlay {#mapwarper}

This map of the county of Kent in the UK uses the standard OSM basemap overlaid with a georeferenced topographic survey map from 1860.
<param ve-map center="51.254, 0.876" zoom="10">
<param ve-map-layer mapwarper active mapwarper-id="44832" title="Kent Topo Survey 1860">

```markdown
<param ve-map center="51.254, 0.876" zoom="10">
<param ve-map-layer mapwarper active mapwarper-id="44832" title="Kent Topo Survey 1860">
```

## Map with flyto actions in essay text {#flyto}

`flyto` actions can be used in the essay text to trigger an update in the map viewer.  The action is triggered by a user mouse click or hover interaction with text that is "wrapped" with an HTML `span` tag defining the action.  This paragraph used a map of <span data-mouseover-map-flyto="43,12.3,6">Italy</span> and includes actions causing the map to flyto <span data-click-map-flyto="41.893,12.483,10" data-mouseover-map-flyto="41.893,12.483,11">Rome</span> or <span data-mouseover-map-flyto="45.440, 12.332, 13">Venice</span> when the mouse hovers over the text.
<param ve-map center="43,12.3" zoom="6">

```markdown
`flyto` actions can be used in the essay text to trigger an update in the map viewer.  The action is triggered by a user mouse click or hover interaction with text that is "wrapped" with an HTML `span` tag defining the action.  This paragraph used a map of <span data-mouseover-map-flyto="43,12.3,6">Italy</span> and includes actions causing the map to flyto <span data-click-map-flyto="41.893,12.483,10" data-mouseover-map-flyto="41.893,12.483,11">Rome</span> or <span data-mouseover-map-flyto="45.440, 12.332, 13">Venice</span> when the mouse hovers over the text.
<param ve-map center="43,12.3" zoom="6">
```
