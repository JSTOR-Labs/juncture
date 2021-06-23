<param ve-config title="Documentation" component="default" class="documentation" fixed-header>

# Essay configuration

## Overview

An optional `ve-config` tag may be added to an essay to define essay-specific attributes, metadata, and behaviors.  For exanple, this tag is often used to define a title and banner image for an essay.  When used, this tag is generally included at the top of the essay markdown file.  In addition to some commonly used metadata like title and author names the ve-config tag can also be used as a convenient means for passing arbitray metadata to various components used by the tool.  This typically includes components like the header and footer but the the metdata is globally accessible to any component.

## Options

- __title__:  The essay title.
- __author__:  Author name(s).  Multiple author names should be separated by a semicolon.
- __banner__:  The URL to an image to use for the banner.  The banner image has a fixed height of 400 pixels.  The banner width is variable and matches the width of the browser window in which it is displayed.  The image used for the banner will be scaled to fit within this area.  As a rule of thumb an image with a width of 1200px and height of 400px works well.
- __layout__:  By default essays are shown with a horizontal layout.  The value `vertical` should be used for this option to display the essay in 2 columns with the text on the left and a visualiation pane on the right.
- __eid__:  The Wikidata entity ID (QID) associated with the Visual Essay entity created for the essay
- __about__:  The Wikidata entity ID of the entity that is the main focus of the essay.  This would generally be a QID for the plant that is discussed.
- __ANY_KEY__:  In addition to the the key-value pairs already described the ve-config tag can be used for defining arbitrary metadata that can be used by any component.  Component-specific metadata defined in the ve-config tag will be identified in the documentation for the specific component.

## Usage examples

### A generic template

```html
<param ve-config
       title="Essay Title"
       author="Essay Author Name"
       banner="URL to banner image"
       layout="vertical"
       eid="Essay Wikidata QID"
       about="Essay Subject Wikidata QID">
```

### Demo essay configs

`ve-config` from the [Simple map example essay](/samples/simple-map.md)

```html
<param ve-config
       title="Hello, Berlin"
       banner="https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/WorldMap-A_with_Frame.png/1024px-WorldMap-A_with_Frame.png"
       layout="vertical"
       eid="Q104699604">
```
