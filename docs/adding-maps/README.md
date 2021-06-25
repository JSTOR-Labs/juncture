<param ve-config title="Documentation" component="default" class="documentation" fixed-header>

# Adding a Map to Your Essay

<param ve-entity eid="Q12439" title="Detroit">
<param ve-map center="Q12439" title="Detroit" zoom="11" prefer-geojson>

To include a basic map in a section of your essay, use the `<param ve-map>` tag:

```html
<param ve-map center="Q12439" title="Detroit" zoom="11">
```

The Wikidata entity identifier for Detroit is "Q12439". We supply this identifier to the `center` attribute. In this example, we have also included a `title` attribute so we can remember what the entity is. This is only for our benefit; it doesn't change the map in any fashion. We could, for example, have made the title "American-Canadian Border" and it would have pointed to the same entity location for Detroit.

Finally, we have included a zoom level of "11". As that number increases, we will zoom in closer to street level. As it decreases, our map will show whole countries, continents, and then the globe.

After the map has rendered at our defined level, readers also have the option to zoom in, zoom out, and move the map at will.



____
[<i class="fas fa-arrow-circle-left"></i> Home](/docs)
