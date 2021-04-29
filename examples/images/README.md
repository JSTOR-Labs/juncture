<!-- This just provides a convenient way for viewing the visual essay, it is not actually needed in the essay -->
<a href="https://essays.juncture-digital.org"><img src="https://gitcdn.link/repo/jstor-labs/juncture/main/images/ve-button.png"></a>

<!-- Some config data for the essay -->
<param ve-config title="Image Viewer Examples" layout="vtl">

# Juncture Image Viewer

- [Basic usage](#basic-usage)
- [Image fit](#fit)

## Basic usage {#basic-usage}

[Wikimedia commons](https://commons.wikimedia.org/wiki/Main_Page) is a media file repository making available public domain and freely-licensed educational media content (images, sound and video clips) to everyone, in their own language. It acts as a common repository for the various projects of the Wikimedia Foundation, but you do not need to belong to one of those projects to use media hosted here. The repository is created and maintained not by paid archivists, but by volunteers.  As of December 2020, Wikimedia Commons contains over 66 million freely usable media files.
<param ve-image url="https://upload.wikimedia.org/wikipedia/commons/3/37/Mud_Cow_Racing_-_Pacu_Jawi_-_West_Sumatra%2C_Indonesia.jpg" description='Two bulls running while the jockey holds on to them in pacu jawi (from Minangkabau, "bull race"), a traditional bull race in Tanah Datar, West Sumatra, Indonesia. 2015, Final-45.' attribution="Rodney Ee" license="CC BY 2.0">

```html
<param ve-image url="https://upload.wikimedia.org/wikipedia/commons/3/37/Mud_Cow_Racing_-_Pacu_Jawi_-_West_Sumatra%2C_Indonesia.jpg" description='Two bulls running while the jockey holds on to them in pacu jawi (from Minangkabau, "bull race"), a traditional bull race in Tanah Datar, West Sumatra, Indonesia. 2015, Final-45.' attribution="Rodney Ee" license="CC BY 2.0">
```

This is the same image referenced by the generated manifest.
<param ve-image fit="cover" manifest="https://iiif-v2.visual-essays.app/manifest/067989e912341a67401ceed78be530af83a206d8cab37a7ff8b46a2bd1b49c62">

```html
<param ve-image fit="cover" manifest="https://iiif-v2.visual-essays.app/manifest/067989e912341a67401ceed78be530af83a206d8cab37a7ff8b46a2bd1b49c62">
```

## Setting image fit {#fit}

### Cover

In this example the image is displayed using the `fit="cover"` attribute which scales the image to completely fill the available viewer area. This is the default fit mode for the viewer and this attribute can be ommitted if this is the desired behavior.
<param ve-image fit="cover" manifest="https://iiif-v2.visual-essays.app/manifest/067989e912341a67401ceed78be530af83a206d8cab37a7ff8b46a2bd1b49c62">

```html
<param ve-image fit="cover" manifest="https://iiif-v2.visual-essays.app/manifest/067989e912341a67401ceed78be530af83a206d8cab37a7ff8b46a2bd1b49c62">
```

### Contain

The image is displayed using the `fit="contain"` attribute which scales the image such that the entire image fits in the available viewer area. 
<param ve-image fit="contain" manifest="https://iiif-v2.visual-essays.app/manifest/067989e912341a67401ceed78be530af83a206d8cab37a7ff8b46a2bd1b49c62">

```html
<param ve-image fit="contain" manifest="https://iiif-v2.visual-essays.app/manifest/067989e912341a67401ceed78be530af83a206d8cab37a7ff8b46a2bd1b49c62">
```

