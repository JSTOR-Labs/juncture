<param ve-config title="Documentation" component="default" class="documentation" fixed-header>

[<i class="fas fa-arrow-circle-left"></i> Home](/docs) <br />
[Link to a Hosted Image (Preferred)](#link-to-hosted-image) <br />
[Upload an Image to your GitHub Repository (Not Ideal)](#upload-an-image) <br />
[Making an Uploaded Image the Banner for a Single Page/Essay](#single-page-banner) <br />
[Making an Uploaded Image the Main Website Banner](#website-banner) <br />
[Linking Data Entities <i class="fas fa-arrow-circle-right"></i>](/docs/linking-data)
___

# Adding Images to your Site

When adding an image to a page/essay, it is generally best to use the `<param ve-image>` tag. This tag has significant benefits over using basic Markdown such as 
```html
![Image accessibility description goes here](http://exampleurl.com/image.png)
```

By using the `<param ve-image>` tag, your image will automatically be shown in the right-hand pane of your essay within a specialized [Mirador](https://projectmirador.org/) viewer. Mirador has the following benefits:

1. Zoom, display, compare images
2. Create a gallery of images
3. Compare and annotate images
4. Automatic titling

The `<param ve-image>` requires two additional attributes: `title` and `url`. The `title` contains the description of the image which will be displayed underneath and is important for accessibility purposes. The `url` is the address where the image is stored. Here is an example:

```html
<param ve-image title="Roasted Coffee Beans" url="https://upload.wikimedia.org/wikipedia/commons/c/c5/Roasted_coffee_beans.jpg">
```

The `<param ve-image>` tag supports the following image types:

* .png
* .jpg
* .tiff (a high-resolution format, often used in cultural heritage)

We are currently working on support for the .svg filetype. For the `url`, generally it is preferred to link to a hosted image instead of uploading an image to your GitHub Repository.

The `<param ve-image>` supports a variety of additional attributes that are [documented here](/docs/visual-essay-tags/ve-image/).

# Link to a Hosted Image (Preferred)
<param id="link-to-hosted-image">

For most images, this is the best practice. Ideally, the image is hosted on a stable URL of some kind in a cultural heritage collection. If you have a copy of the image and the right to use it, you can also upload it to the [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Images) and link to it there.

# Upload an Image to your GitHub Repository (Not Ideal)
<param id="upload-an-image">

This approach may make sense if you have an image whose rights are cleared, but that is not of general interest to the public (and therefore not appropriate for [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:Images). This makes sense for small, site-specific images like navigation arrows or buttons. Keep in mind that GitHub does enforce limitations on repository (and therefore image) sizes, so any uploaded images should be small in size. 

It is a good practice to create a `/images/` directory in your GitHub repository to hold sitewide images. For images that are likely to appear on a single page, include those images in the directory for that page (alongside the README.md file). 

An ideal use-case for uploading an image to your GitHub repository is for a site (or page) banner.

# Making an Uploaded Image the Banner for a Single Page/Essay
<param id="single-page-banner">

The banner image for a particular page is declared in the `<param ve-config>` tag with the banner attribute:
```html
<param ve-config
  banner="http://example.jpg">
```

[Read more about the attributes](/docs/visual-essay-tags/ve-config/) for the `param ve-config` tag.

When editing a banner image for your site, aim for:

* Height- ~400 pixels
* Width- 1200-1600 pixels
* .jpg file type
* ≤ 150 kb in size

# Making an Uploaded Image the Main Website Banner
<param id="website-banner">

To specify a banner for your whole site, include a link to the image in the `config.json` file for the site, like so:

```html
{
  "title": "Visual Essays Documentation",
  "banner": "/images/banner.jpg",
  "acct": "JSTOR-Labs",
  "repo": "ve-docs",
  "ref": "main",
  "logo": "/images/labs.jpg",
  "favicon": "/images/favicon.ico",
  "css": "https://cdn.jsdelivr.net/gh/jstor-labs/ve-docs@main/css/docs.css",
  "nav": []
}
```

The `config.json` file holds a variety of sitewide settings. [Read more <i class="fas fa-arrow-circle-right"></i>](/docs/config-file-description/)
___
[<i class="fas fa-arrow-circle-left"></i> Home](/docs) | [Linking Data Entities <i class="fas fa-arrow-circle-right"></i>](/docs/linking-data)
