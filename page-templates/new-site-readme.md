<param ve-config title="Page Title" author="Page Author" banner="https://picsum.photos/id/164/1000/400">

# Welcome to your new Juncture site!

This Juncture site is published at [<site-url>](<site-url>) (note that it can take a few minutes for this URL become active after the site is created).
- The content for this site is located in the GitHub repository at [<repo-url>](<repo-url>).

# Customizing your site

- The site home page (this page) can be edited at [<edit-url>](<edit-url>)

A configuration file (**config.yaml**) is located at root of the **juncture** branch in the GitHub repository of the new site and is used to customize the site.  Configuration options include setting up navigation links in the site menu and configuring a contact form.
- The configuration page is found at [<config-url>](<config-url>)

## Setting a default banner, title, and tagline for the site

TODO

## Adding pages to the top level site menu

TODO

## Adding a Contact Form with a custom email

To activate the **Contact Us** form, remove the comment character (**#**) from the beginning of the following lines in the config.yaml file.

```yaml
- label: Contact Us
  icon: envelope
  path: "/contact-us"
```

## Modifying the page layout and styling

A custom stylesheet can be used to alter most any styling on the site.  This includes fonts, font sizes, margins, most anything.  The empty stylesheet (found in **[/css/custom.css](<custom-css-url>)**) is provided for performing these customizations.
