<!-- This just provides a convenient way for viewing the visual essay, it is not actually needed in the essay -->
<a href="https://juncture-digital.org"><img src="https://gitcdn.link/repo/jstor-labs/juncture/main/images/ve-button.png"></a>

<!-- Some config data for the essay -->
<param ve-config title="Image Viewer Examples" layout="vtl">

<a class="nav" href="/examples"><i class="fas fa-arrow-circle-left"></i>Back to examples</a>

# Juncture Image Viewer

- [Basic usage](#basic-usage)
- [Image fit](#fit)

## Basic usage {#basic-usage}

### Girl with a Pearl Earring

[Girl with a Pearl Earring](https://en.wikipedia.org/wiki/Girl_with_a_Pearl_Earring) (Dutch: Meisje met de parel) is an oil painting by Dutch Golden Age painter Johannes Vermeer, dated c. 1665. Going by various names over the centuries, it became known by its present title towards the end of the 20th century after the earring worn by the girl portrayed there. The work has been in the collection of the Mauritshuis in The Hague since 1902 and has been the subject of various literary treatments. In 2006, the Dutch public selected it as the most beautiful painting in the Netherlands.
<param ve-image label="Girl with a Pearl Earring" description="painting by Johannes Vermeer" license="public domain" url="https://upload.wikimedia.org/wikipedia/commons/0/0f/1665_Girl_with_a_Pearl_Earring.jpg">

```html
<param ve-image label="Girl with a Pearl Earring" description="painting by Johannes Vermeer" license="public domain" url="https://upload.wikimedia.org/wikipedia/commons/f/fa/Girl_with_a_Pearl_Earring_%28Full_Renovation%29.jpg">
```

This is the same image referenced by the generated manifest.
<param ve-image fit="cover" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">

```html
<param ve-image fit="cover" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">
```

### Wikimedia Commons

[Wikimedia commons](https://commons.wikimedia.org/wiki/Main_Page) is a media file repository making available public domain and freely-licensed educational media content (images, sound and video clips) to everyone, in their own language. It acts as a common repository for the various projects of the Wikimedia Foundation, but you do not need to belong to one of those projects to use media hosted here. The repository is created and maintained not by paid archivists, but by volunteers.  As of December 2020, Wikimedia Commons contains over 66 million freely usable media files.

<param ve-image fit="cover" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">

## Image options {#options}

### Image fit {#fit}

#### Cover {#fit-cover}

In this example the image is displayed using the `fit="cover"` attribute which scales the image to completely fill the available viewer area. This is the default fit mode for the viewer and this attribute can be ommitted if this is the desired behavior.
<param ve-image fit="cover" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">

```html
<param ve-image fit="cover" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">
```

#### Contain {#fit-contain}

The image is displayed using the `fit="contain"` attribute which scales the image such that the entire image fits in the available viewer area. 
<param ve-image fit="contain" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">

```html
<param ve-image fit="contain" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">
```

### Region {#region}

The image is displayed using the `region="x,y,w,h"` attribute which defines the region within the image to show.  This can be combined with the `fit` attribute. 
<param ve-image region="7271,7605,814,923" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">

```html
<param ve-image region="7271,7605,814,923" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">
```

### Rotate {#rotate}

The `rotate` attribute will rotate an image.  This example rotates the image 90 degrees.
<param ve-image rotate="90" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">

```html
<param ve-image rotate="90" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">
```

Image rotated 180 degrees.
<param ve-image rotate="180" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">

```html
<param ve-image rotate="180" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">
```

Image rotated 270 degrees.
<param ve-image rotate="270" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">

```html
<param ve-image rotate="270" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">
```

Image rotated 45 degrees.
<param ve-image rotate="45" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">

```html
<param ve-image rotate="45" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">
```

Rotate and region options combined.
<param ve-image rotate="45" region="4729,1946,7626,5138" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">

```html
<param ve-image rotate="45" region="4729,1946,7626,5138" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">
```

### Zoomto {#zoomto}

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea <span data-click-image-zoomto="3607,4314,4238,4061">commodo consequat</span>. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia <span data-mouseover-image-zoomto="6914,6799,1472,2820">deserunt mollit</span> anim id est laborum.
<param ve-image fit="cover" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">

```html
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea <span data-click-image-zoomto="3607,4314,4238,4061">commodo consequat</span>. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia <span data-mouseover-image-zoomto="6914,6799,1472,2820">deserunt mollit</span> anim id est laborum.
<param ve-image fit="cover" manifest="https://iiif.juncture-digital.org/manifest/6dd738aed85597cac540ad31dd5818e86ef7f2918c7b43a9eb3123d5538e6e4c">
```
