<param ve-config title="Documentation" component="default" class="documentation" fixed-header>

# Map viewer

## Overview

The `ve-map` tag indicates that a map should be added as a visualization component for the associated text element(s).  Maps can be further customized with `ve-map-layer` directives that define layers or overlays to be applied to the map. 

## Options

- __basemap__:  By default, [OpenStreetMap (OSM)](https://www.openstreetmap.org/) is used for the base map.  Other base maps are available and can be requested with this attribute.  The available base maps are:
    - [`OpenSteetMap`](https://leaflet-extras.github.io/leaflet-providers/preview/#filter=OpenStreetMap.Mapnik)  
    - [`OpenTopoMap`](https://leaflet-extras.github.io/leaflet-providers/preview/#filter=OpenTopoMap)  
    - [`Stamen_Watercolor`](https://leaflet-extras.github.io/leaflet-providers/preview/#filter=Stamen.Watercolor)  
    - [`Stamen_TerrainBackground`](https://leaflet-extras.github.io/leaflet-providers/preview/#filter=Stamen.TerrainBackground)  
    - [`Stadia_AlidadeSmooth`](https://leaflet-extras.github.io/leaflet-providers/preview/#filter=Stadia.AlidadeSmooth)  
    - [`Stadia_AlidadeSmoothDark`](https://leaflet-extras.github.io/leaflet-providers/preview/#filter=Stadia.AlidadeSmoothDark)  
    - [`Esri_WorldPhysical`](https://leaflet-extras.github.io/leaflet-providers/preview/#filter=Esri.WorldPhysical)    
    - [`Esri_WorldGrayCanvas`](https://leaflet-extras.github.io/leaflet-providers/preview/#filter=Esri.WorldGrayCanvas)
    - [`Esri_NatGeoWorldMap`](https://leaflet-extras.github.io/leaflet-providers/preview/#filter=Esri.NatGeoWorldMap)
- __center__:  This attribute defines the center point for the map.  The center point can be defined as a latitude and longitude coordinates or using a QID for an entity that is associated with geo-coordinates.  For instance, the following are equivalent.  They both use the city of Ann Arbor, Michigan as the map center point.  In the first version the latitude and longitude coordinates are specified and in the second the Wikidata QID for Ann Arbor is provided. 
    ```html
    <param ve-map center="42.2813, -83.7483">
    <param ve-map center="Q485172">
    ```
- __zoom__:  This attribute defines the starting map zoom level.  This number can be expressed in 0.1 increments, such as `zoom="3.4"`
- __show-labels__:  By default, the labels for any locations plotted on a map (both markers and GeoJSON features) are not automatically displayed when the map is loaded.  This attribute can be used to override this default behavior and show labels on loading.  Note that a user can still open the label by hovering over and/or clicking on the label or GeoJSON defined region.
- __prefer-geojson__:  Location entities are automatically added to a map components that is visible for an active text element.  By default the location is represented as a marker pinned at a discrete geo-coordinate.  However, many location entities in the Wikidata knowledge graph can also be associated with GeoJSON shape files that represent the location as region using a polygon shape.  If the visualization of a location on a map using the GeoJSON defined region is preferred over a simple marker/pin this attribute is used to express that preference.

The following attributes are used for the time dimension control and animation.  This functionality is provided by the Leaflet TimeDimension plugin.  Refer to [Leaflet.TimeDimension](https://github.com/socib/Leaflet.TimeDimension) for more details on the options.

- __time-dimension__:  Set to `true` to enable the time dimension controls.  When enabling the time dimension the input data is expected to include a `time` property in the feature properties object.
- __data__:  URL to GeoJSON or delimited (.csv or .tsv) file with time data.  GeoJSON files may also be loaded using the `ve-map-layer` tag.
- __time-interval__:  String to construct the first available time and the last available time. Format: [ISO8601 Time inverval](https://en.wikipedia.org/wiki/ISO_8601#Time_intervals)
- __duration__:  Period of time which the features will be shown on the map after their time has passed. If null, all previous times will be shown. Format: [ISO8601 Duration](https://en.wikipedia.org/wiki/ISO_8601#Durations)
- __max-zoom__:  The maximum zoom level to use when auto-fit is enabled.  Default=`16`
- __date-format__:  Format to use for the date/time in the time dimension control.  Default=`YYYY-MM-DD` (refer to https://momentjs.com/docs/#/displaying/)
- __auto-play__:   Animate the map automatically.  Default=`false`
- __auto-fit__:  When running the animation automatically resize the viewing area to fit all active points.  Default=`false`
- __loop__:  Loop the animation when `auto-play` is enabled.  Default=`false`
- __fps__:  Animation speed.  Default=`1`fps

The following attributes control marker and geojson formatting:

- __marker-style__:  `circle` or `pin` - default = `pin`
- __radius__:  Marker radius when `marker-style` is set to `circle`.  Default=`4`
- __marker-symbol__:  A [Fontawesome icon](https://fontawesome.com/icons?d=gallery) label.  Default=`circle`
- __marker-color__:  Default=`#2C84CB`
- __opacity__:  Marker opacity.  Default=`1`
- __marker-symbol-color__:  Default=`#FFF`
- __marker-symbol-xoffset__: Default=`0`
- __marker-symbol-yoffset__:  Default=`0`
- __stroke__:  Line color.  Default=`'#FB683F'`
- __stroke-width__ :  Marker/GeoJSON feature line width.
- __stroke-opacity__:  Default=`0`
- __fill__:  Fill color.  Default=`#32C125`
- __fill-opacity__:  Default=`0.5`

### Interactions

- __flyto__:  The `flyto` action takes a comma-delimited value consisting latitude, longitude, and zoom level.  
Below are example `flyto` actions for Rome, one for a `click` event and another for a `mouseover` (hover) event:  
```html 
	<span data-click-map-flyto="41.893,12.483,11">Rome</span>
	<span data-mouseover-map-flyto="41.893,12.483,11">Rome</span>
```

## Usage examples

```html
	<param ve-map center="32.262084, 64.391554" zoom="2.5" stroke-width="0" show-labels>
	<param ve-map-layer geojson url="/geojson/peony.json" title="Peony Distribution" active> 
```

```html
	<param ve-map center="0.040297, -71.224280" zoom="3.8" marker-type="circle" stroke-width="0" fill-opacity="1">
	<param ve-map-layer geojson active title="Aurea" url="https://jstor-labs.github.io/plant-humanities/data/heliconia-aurea.tsv" fill="#D11141" radius="6">  
	<param ve-map-layer geojson active title="Bihai" url="https://jstor-labs.github.io/plant-humanities/data/heliconia-bihai.tsv" radius="4.5" fill="#009900"> 
```

