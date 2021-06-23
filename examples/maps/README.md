<a href="https://juncture-digital.org"><img src="https://gitcdn.link/repo/jstor-labs/juncture/main/images/ve-button.png"></a>

<param ve-config
       title="Map examples"
       banner="https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/WorldMap-A_with_Frame.png/1024px-WorldMap-A_with_Frame.png"
       layout="vtl"
       author="JSTOR Labs team">

<a class="nav" href="/examples"><i class="fas fa-arrow-circle-left"></i>Back to examples</a>

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

Example map with a map title, custom base layer, 2 GeoJSON layers and an auto-generated marker with a Fontawesome icon and custom color.
<param title="Nicaragua" eid="Q811" fill="#92086D" marker-symbol="user">
<param ve-map title="Girolamo Benzoni's Accounts Refer to Cacao Being Grown in Nicaragua" center="12.316683, -84.946184" zoom="5" basemap="Esri_WorldPhysical">
<param ve-map-layer geojson active title="Central American Neotropics" url="Neotropics.geojson">
<param ve-map-layer geojson active title="Nicaragua" url="Nicaragua.geojson">

```markdown
<param title="Nicaragua" eid="Q811" fill="#92086D" marker-symbol="user">
<param ve-map title="Girolamo Benzoni's Accounts Refer to Cacao Being Grown in Nicaragua" center="12.316683, -84.946184" zoom="5" basemap="Esri_WorldPhysical">
<param ve-map-layer geojson active title="Central American Neotropics" url="Neotropics.geojson">
<param ve-map-layer geojson active title="Nicaragua" url="Nicaragua.geojson">
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

## Map with heatmap overlay {#heatmap}

This example uses the [Leaflet Heatmap Layer Plugin](https://www.patrick-wied.at/static/heatmapjs/plugin-leaflet-layer.html) to add a heatmap overlay on a map.  `ve-map-layer` options:
- **heatmap** - _required_
- **url** - _required_ URL to dataset file, currently assumes this is a TSV tile. 
- **radius** - _optional_ (integer, default 15) Defines the radius of your datapoints. If scaleRadius is false, radius is measured in pixels. If scaleRadius is true it's measured in the scale of the map
- **max-opacity** - _optional_ (float, default 0.6)
- **scale-radius** - _optional_ (boolean, default false) Defines whether the radius should be scaled to accordingly to zoom level.
- **use-local-extrema** - _optional_ (boolean, default false) Defines whether the heatmap should use a global extrema set via setData/addData OR a local extrema (the maximum and minimum of the currently displayed viewport)
- **max** - _optional_ (integer, default 10) Sets the upper bound of your dataset
<param ve-map center="-2, 118" zoom="4">
<!-- <param ve-map-layer heatmap url="nepenthes_horticultural_heatmap.tsv" radius="2" scale-radius="true" use-local-extrema="true" max-opacity="0.6"> -->

```markdown
<param ve-map center="-2, 118" zoom="4">
<param ve-map-layer heatmap 
       url="nepenthes_horticultural_heatmap.tsv" 
       radius="2" 
       scale-radius="true" 
       use-local-extrema="true" 
       max-opacity="0.6">
```

## Map with custom markers or images {#custom-markers}

This example uses a [Leaflet Icon](https://leafletjs.com/examples/custom-icons/) to put an image on the map. The basic tag is `<param ve-map-marker>` and the options are:
- **url** - _required_ URL to image.
- **center** - _required_ latitude and longitude coordinates for the image placement, in that order, separated by a comma. For example: `"39, 20"`
- **size** - _required_ the size of the image in pixels, separated by a comma.
- **circle** - when set to "true", the image is cropped to an icon-sized circle
- **square** - when set to true, the image is cropped to an icon-sized square
- **iconAnchor** - The coordinates of the "tip" of the icon (relative to its top left corner). The icon will be aligned so that this point is at the marker's geographical location. Centered by default.
- **shadowUrl** - the URL to a shadow image.
- **shadowSize** - the size of the shadow image in pixels, separated by a comma.
- **shadowAnchor** - The coordinates of the "tip" of the shadow (relative to its top left corner) (the same as iconAnchor if not specified).
- **className** - A custom class name to assign to both primary and shadow images. Used for custom CSS styling.
<param ve-map center="2, 40" zoom="3">
<!--
<param ve-map-marker
       url="https://leafletjs.com/examples/custom-icons/leaf-green.png"
       coords="17.188263050774324, 52.28406397248149"
       size="38, 95"
       iconAnchor="22, 94"
       shadowUrl="https://leafletjs.com/examples/custom-icons/leaf-shadow.png"
       shadowSize="50, 64">
<param ve-map-marker url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Pinz%C3%B3n_azul_de_Gran_Canaria_%28macho%29%2C_M._A._Pe%C3%B1a.jpg/220px-Pinz%C3%B3n_azul_de_Gran_Canaria_%28macho%29%2C_M._A._Pe%C3%B1a.jpg"
       coords="-7.182405194219532, 35.05200886854757"
       size="129, 170"
       circle="true">
-->

```markdown
<param ve-map center="2, 40" zoom="4">
<param ve-map-marker
       url="https://leafletjs.com/examples/custom-icons/leaf-green.png"
       coords="17.188263050774324, 52.28406397248149"
       size="38, 95"
       iconAnchor="22, 94"
       shadowUrl="https://leafletjs.com/examples/custom-icons/leaf-shadow.png"
       shadowSize="50, 64">
<param ve-map-marker
       url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Pinz%C3%B3n_azul_de_Gran_Canaria_%28macho%29%2C_M._A._Pe%C3%B1a.jpg/220px-Pinz%C3%B3n_azul_de_Gran_Canaria_%28macho%29%2C_M._A._Pe%C3%B1a.jpg""
       coords="-7.182405194219532, 35.05200886854757"
       size="129, 170"
       circle="true"
       >
```
