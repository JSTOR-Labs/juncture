<param ve-config component="default" fixed-header="true" logo="/images/logo-juncture.svg">
<param nav label="Contact Us" action="contact-us" icon="fas fa-envelope">
<param nav label="Documentation" action="load-page" path="/docs" icon="fas fa-envelope">
<param nav label="View page markdown" action="view-markdown" icon="fas fa-file-code">
<param nav if-authenticated>
<param nav if-authenticated label="Edit this page" action="edit-page" icon="fas fa-edit">
<param nav if-authenticated label="Add a page" action="add-page" icon="fas fa-file-medical">
<param nav if-authenticated label="Goto to GitHub" action="goto-github" icon="fab fa-github">
<param nav if-authenticated if-admin>
<param nav if-authenticated if-admin label="Create new site" action="create-site" icon="fas fa-plus-circle">
<param nav if-authenticated if-admin label="Software update" action="software-update" icon="fas fa-wrench">

# Welcome to Juncture
<param id="welcome">

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

This page provides simple instructions for performing some common Juncture actions

1. [Creating a sample visual essay](#create-visual-essay)
2. [Creating a new Juncture site](#create-juncture-site)

# Creating your first visual essay
<param id="create-visual-essay" class="cards clamp-20">

A visual essay may be created in any existing Github repository.  This can be done directly from the Github web site or using simple tools provided on the Juncture site.  In this example we will use the Juncture approach.  Instructions for creating visual essays directly in Github may be found in the [documentation](/docs/create-visual-essay-in-github).

## Login with your Github account

![](/images/login-with-github.jpg)

1. If you don't have a Github account, create a free one at [github.com](https://github.com). 
2. Login using the Juncture menu.  The first time you login to Juncture with Github you will be asked to grant access to the Juncture application.  This step will not be required in subsequent sessions.

## Create a sample visual essay

![](/images/sample-essay.jpg)

1. From the Juncture menu select the `Add a page` option
2. In the dialog form select an existing Github repository to use for the visual essay and a name for the essay
3. After creation, the browser page will refresh to display the new essay.  The sample essay includes a high resolution (IIIF) image of the _Girl with a Pearl Earring_ painting, an interactive map, and a few other examples of commonly used visual essay features.

## Modify the sample essay

![](/images/edit-visual-essay.jpg)

1. From the Juncture menu select the `Edit this page` option
2. A new window will be displayed with the Github editor enabled
3. Change essay text and tags as desired
4. Save the edits by selecting the green Github `Commit changes` button located at the bottom of the page

## View the visual essay

![](https://upload.wikimedia.org/wikipedia/commons/6/67/Learning_Curve_--_Coming_Soon_Placeholder.png)

1. Reload the visual essay window using the browser reload button

# Creating a Juncture site
<param id="create-juncture-site" class="cards clamp-20">

In addition to converting single text files into visual narratives, Juncture can also be used to create full web sites consisting of multiple visual essays with navigation, site info pages (_About_, _Contact us_, etc), email contact form, logo, and other simple customizations.

## Login with your Github account

![](/images/login-with-github.jpg)

1. If you don't have a Github account, create a free one at [github.com](https://github.com). 
2. Login using the Juncture menu.  The first time you login to Juncture with Github you will be asked to grant access to the Juncture application.  This step will not be required in subsequent sessions.

## Create a new Juncture site

![](https://upload.wikimedia.org/wikipedia/commons/6/67/Learning_Curve_--_Coming_Soon_Placeholder.png)

1. From the Juncture menu select the `Create a new site` option
2. In the dialog form enter the name of the Juncture site (Github repository) to create.
3. After creation, the browser page will refresh to display the home page for the new site.

## Customize the new site

![](https://upload.wikimedia.org/wikipedia/commons/6/67/Learning_Curve_--_Coming_Soon_Placeholder.png)

1. Lorem ipsum dolor sit amet
2. Consectetur adipiscing elit
3. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua

#
<param class="footer">

- Brought to you by: [![JSTOR labs](/images/Labs_logo_knockout.svg "JSTOR Labs")](https://labs.jstor.org)
- [About](about)
- [Terms and conditions](terms-and-conditions)
