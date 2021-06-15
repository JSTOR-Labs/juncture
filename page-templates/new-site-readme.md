<a href="https://juncture-digital.org"><img src="https://gitcdn.link/cdn/jstor-labs/juncture/main/images/ve-button.png"></a>

<param ve-config title="Page Title" author="<<display-name>>" banner="https://picsum.photos/id/164/1000/400">

# Welcome to your new Juncture site!

This Juncture site is published at [https://<<acct>>.github.io/<<repo>>](https://<<acct>>.github.io/<<repo>>) (note that it can take a few minutes for this URL become active after the site is created).
- The content for this site is located in the GitHub repository at [https://github.com/<<acct>>/<<repo>>](https://github.com/<<acct>>/<<repo>>).
- A sample visual essay can be found at [https://github.com/<<acct>>/<<repo>>/sample](/sample).

# Customizing your site

- The site home page (this page) can be edited at [<<edit-url>>](<<edit-url>>)
- The sample essay can be edited at [https://github.com/<<acct>>/<<repo>>/edit/main/sample/README.md](https://github.com/<<acct>>/<<repo>>/edit/main/sample/README.md)

A configuration file (**config.yaml**) is located at root of the **juncture** branch in the GitHub repository of the new site and is used to customize the site.  Configuration options include setting up navigation links in the site menu and configuring a contact form.
- The configuration page is found at [https://github.com/<<acct>>/<<repo>>/blob/juncture/config.yaml](https://github.com/<<acct>>/<<repo>>/blob/juncture/config.yaml)

## Setting a default banner, title, and tagline for the site

At the top of the configuration file are a number of options for customizing the site display.

```yaml
title: Juncture
tagline: A Visual Essay Site
banner: https://picsum.photos/id/164/1000/400
favicon: /images/favicon.svg
```

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

A custom stylesheet can be used to alter most any styling on the site.  This includes fonts, font sizes, margins, most anything.  The empty stylesheet (found in **[/css/custom.css](https://github.com/<<acct>>/<<repo>>/blob/main/css/custom.css)**) is provided for performing these customizations.

# Providing access to content creators

Initially, only the site creator (<<acct>>) is able to add content to the site.  The `Manage access` panel on the GitHub `Settings` page is used to provide write or admin access to other users.  In this panel enter the GitHub usernames any other users that will be adding content or managing the site.
- The `Manage access` panel for this site is found at [https://github.com/<<acct>>/<<repo>>/settings/access](https://github.com/<<acct>>/<<repo>>/settings/access)