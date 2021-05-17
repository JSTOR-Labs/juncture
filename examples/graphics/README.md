<a href="https://juncture-digital.org"><img src="https://gitcdn.link/repo/jstor-labs/juncture/main/images/ve-button.png"></a>

<param ve-config
       title="Graphics examples"
       banner="https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/WorldMap-A_with_Frame.png/1024px-WorldMap-A_with_Frame.png"
       layout="vtl"
       author="JSTOR Labs team">

<a class="nav" href="/examples"><i class="fas fa-arrow-circle-left"></i>Back to examples</a>

## Introduction
The Graphic viewer is used to display images, GIFs, and SVGs. This component is used to display graphics that do not require IIIF capabilites. The basic tag is
```html
<param ve-graphic img="https://upload.wikimedia.org/wikipedia/commons/a/ad/SunflowerModel.svg">
```
<param ve-graphic img="https://upload.wikimedia.org/wikipedia/commons/a/ad/SunflowerModel.svg">

###
An optional `title` attribute can be added to the graphic tag to display a caption.
```html
<param ve-graphic img="https://upload.wikimedia.org/wikipedia/commons/a/ad/SunflowerModel.svg" title="Sunflower">
```
<param ve-graphic img="https://upload.wikimedia.org/wikipedia/commons/a/ad/SunflowerModel.svg" title="Sunflower">
