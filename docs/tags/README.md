<param ve-config title="Documentation" component="default" class="documentation" fixed-header>

# Visual essay tags

Essay visualizations are created (and optionally controlled) by a couple of special HTML tags that are added to the essay markdown text.  Two HTML tags are currently used.

- The __param__ tag is used to define visualizations that are associated with an essay section or paragraph.  The `param` tags all start on a new line and include attributes defining the specific visualization to create and all required options.
- The __span__ tag is used to wrap sections of text in the essay to associate the text with an entity or to use the text as a interaction trigger.  An example of an interaction trigger would be connecting a location reference in the essay text to an interaction that causes the map to "fly to" a specific location when the user clicks on or hovers over the "spanned" text in the essay.

HTML tags begin with the `<` character and end with the `>` character.  The text after the `<` character and before the first space define the tag name.  The HTML language defines many tags but the visual essay tool only uses the `param` and `span` tags.  Both of these are standard HTML tags that have been extended for use by the visual essay tool.  In the case of the `param` tag a visual essay type attribute and optional options attributes are used to define the type of visualization generated.  The visual essay type attribute starts with `ve-` and defines the specific component used to render the visualizaiton.  Below are a few commonly used `ve` type attributes.

- `ve-image`
- `ve-map`
- `ve-video`

More detailed information on these tags and others are provided in the following sections.

## Configuration and data tags

The two tags in this section, the `ve-config` and `ve-entity` tags, do not directly correspond to a specific visualization but rather are used to provide general data that guides the overall rendering of the essay.  The `ve-config` tag is used to define overall formatting and essay-level metadata such as title and author name(s).  The `ve-entity` tag is used to identify entities (people, locations, organizations, taxon elements, etc) that are referenced in or otherwise applicable to the essay text.  Data associated with entities identified by a ve-entity tag is retrieved from an external knowledge graph. 

- [Essay configuration](ve-config)
- [Entity declaration](ve-entity)

## Visualization component tags

The tags in this section are used to declare and configure one or multiple visualizers that are associated with an essay section or paragraph.

- [Image viewer](ve-image) - <i class="fas fa-image"></i>
- [Map viewer](ve-map) - <i class="fas fa-map-marker-alt"></i>
- [Map layer](ve-map-layer) - <i class="fas fa-map-marker-alt"></i>
- [Video viewer](ve-video) - <i class="fas fa-video"></i>
- [Network viewer](ve-network) - <i class="fas fa-chart-network"></i>
- [Plant specimen viewer](ve-plant-specimen) - <i class="fas fa-seedling"></i>
- [Tabular data viewer](ve-table) - <i class="fas fa-table"></i>
- [Knightlab timeline viewer](ve-knightlab-timeline) - <i class="fas fa-history"></i>
- [Graphic viewer](ve-graphic) - <i class="fas fa-file-image"></i>
- [Storiiies viewer](ve-storiiies) - <i class="fas fa-book"></i>

