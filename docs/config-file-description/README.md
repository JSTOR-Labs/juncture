<param ve-config title="Documentation" component="default" class="documentation" fixed-header>

[<i class="fas fa-arrow-circle-left"></i> Home](/docs)
___
The `config.json` file stores sitewide settings such as the site title, logo, and banner. The `config.json` file should be created in the root directory of your GitHub repository. It takes the general form:

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

The `config.json` file contains a set of key/value pairs inside a set of brackets `{}`. Both the key and value are written in quotations marks with a single colon between them.

|Key|Value|Purpose|
|---|---|---|
|`title`|The title for your site|This title will be displayed at the top of each page on your site|
|`banner`|The link to your banner image|This banner image is displayed on any page where a banner has not specificed using the `ve-config` tag|
|`acct`|The GitHub account where the repository is stored| ? |
|`repo`|The GitHub repository name for the site| ? |
|`ref`| ? | ? |
|`logo`|The link to a logo image for your site|This image will be displayed as the site logo|
|`favicon`|The link to a favicon file (.ico)|Displays a small icon in browser tabs for the website|
|`css`|A link to the site stylesheet (.css)|Changes the default styling for your site|
|`nav`|A list of additional navigation links|Adds additional links to the hamburger menu|

___
[<i class="fas fa-arrow-circle-left"></i> Home](/docs)
