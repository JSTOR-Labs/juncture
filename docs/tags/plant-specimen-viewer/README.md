<param ve-config title="Documentation" component="default" class="documentation" fixed-header>

# Plant specimen viewer

## Overview
![Plant Specimen Viewer](plantspecimen.png){: .right .dropshadow .border .thumb-300w} 
The plant specimen viewer is used to display a high resolution image for a plant type specimen retrieved from the [Global Plants](https://https://plants.jstor.org) database.

## Options
- __eid__:  The Wikidata QID for a species-level taxon name.  For example, [Q12844029](https://www.wikidata.org/entity/Q624242)
- __max__: The maximum number of specimens to return
- __reverse__:  Reverses the date sorting within a type group (holotype, isotype, etc).  By default, multiple specimens within the same type group are sorted by date in ascending order (oldest is first).  Setting this attribute to `true` will display the most recent first.

## Usage examples
```html
<param ve-plant-specimen eid="Q12844029" max="1" reverse="true" type="Holotype">
```
