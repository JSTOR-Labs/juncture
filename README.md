[Juncture](https://essays.juncture-digital.org) is a free service for easily turning a simple text file into an engaging `visual essay`.  A visual essay is an interactive web page that enriches a text narrative with visual elements to provide depth and context.  Juncture does not require special tooling or technical expertise.  It uses the free Github site for hosting and managing the visual essay text files.

In addition to converting single text files into visual narratives, Juncture can also be used to create rich web sites consisting of multiple visual essays with navigation, site info pages (_About_, _Contact us_, etc), email contact form, logo, and other simple customizations.  The creation of a custom visual essay site involves a couple of easy steps than can be accomplished in just a few minutes using a predefined site template (this repository). 

# Getting started with Juncture

## Create a free Github account

The only prerequisite for using Juncture is access to a Github account.  Github is a site commonly used for managing files on the web.  Github has many advanced features for managing and tracking multiple versions of files and is popular with individuals and teams developing open source software.  While the version management capabilities in Github are quite useful and can be used with visual essays, in the typical case it is only used as simple file hosting service, similar to how Dropbox or Google Drive might be used for managing documents and photographs.

If you don't yet have a Github account a free one can be created at [https://github.com](https://github.com).

## Create a Github repository for your visual essays

After creating and signing in to your Github account select the option for creating a new repository.  This should appear as a green _New_ button.  After clicking the new repository button a form will be displayed allowing for a repository name and (optional) description to be provided.  Other options are also available in the creation form.  The repository name can be anything you choose.  In this example will be using _essays_.  After entering a repository name and description ensure the _public_ and _Add a README file_ options are selected and press the green _Create Repository_ button.  That's it, we now have a place to store visual essays and a first skeletal essay (the automatically created _README.md_ file).

## Creating a simple visual essay

When creating a Github repository a `README.md` file is typically generated as part of the repository creation process.  If so, your first visual essay has already been created.  If not, at this point you will need to add a README.md file to your repository.  To create a new _README.md_ file (or any file for that matter) navigate to the repository home page in the Github interface and select _Create new file_ from the _Add file_ menu option.  Enter _README.md_ in the _Name your file..._ field in the generated form and then press the green _Commit new file_ button at the bottom of the page

A visual essay file can be named anything but must have a `.md` file extension.  In this example we will use a README.md file, which is considered the _root_ or _default_ visual essay for a repository (or a sub-folder in a repository).

## Creating a visual essay site

For many users creating and using stand-alone visual essays is sufficient.  The visual essay text files created can be stored in any Github account and displayed using the Juncture service.  For users interested in creating a full web site consisting of multiple visual essays this section provides a few simple steps to get started.

### 1. Create a copy of the Juncture site template

First, ensure that you have signed into your Github account.  Then, navigate to the Github repository containing the Juncture site template repository at [https://github.com/JSTOR-Labs/juncture-site](https://github.com/JSTOR-Labs/juncture-site).  At the top-right of this page press the
_Fork_ button.  _Forking_ a repository creates an exact copy in your personal Github account.  The copy will be created with the same repository name as the original (in this case, _juncture-site_) but can easily be changed in the copied version. 

### 2. Update site configuration file

A configuration file provided in the template allows of easy customization of the site, including designation of a custom title, the use of a custom banner image, customization of the navigation menu, and the setup of an email-based contact form.  The Juncture site template provides instructions for customizing a cloned (_forked_) version of the site.  

### 3. Optional: Configure site as a Github Pages site

_Github Pages_ is an option provided in Github for converting a repository into a simple web site.  When configuring a repository to use Github Pages the base URL for a web site will be of the form `https://GITHUB_ACCOUNT.github.io/REPOSITORY_NAME` where _GITHUB_ACCOUNT_ is your Github account/username and _REPOSITORY_NAME_ is the name of the Github repository used.

Configuring a repository to use Github Pages is accomplished in the _Settings_ page available from the repository home page.

### 4. Optional: Use a custom domain for your site

A Github Pages site can be further configured to use a custom domain instead of the default _https://GITHUB_ACCOUNT.github.io/REPOSITORY_NAME_ for the base URL.

`Juncture` is a free service for easily turning a simple text file into an engaging *visual essay*.  A visual essay is an interactive web page that enriches a text narrative with visual elements to provide depth and context.  Juncture does not require special tooling or technical expertise.  It uses the free Github site for hosting and managing the visual essay text files.

# The template files

# Home page

The web site home page is defined in the `README.md` file (this file) located in the repository root.

## Sample essays

This site template includes a couple of example visual essays, one using the single file approach that is typically used for creating simple essays, and another essay using the folder convention which is often used when creating essays when custom images and other resources are used.

- [Sample essay 1](/example-essay-1) - This sample essay is defined using a single Markdown file.  
- [Sample essay 2](example-essay-2) - This sample essay is defined using folder enabling custom resource files (images, map overlays, etc) to be easily grouped with the essay text (in a README.md Markdown file).

## Sample site info files

- about.md - The template is preconfigured with an _About_ page that can be selected from the site navigation menu in the header.

## Site configuration

The `config.yaml` file is used to set configurable site options such as title and the default banner image. 

## Other template files

In addition to the home page, sample essays, site info files, and site configuration file, the following files are also included in the template repository.  These are essential for the operation of the site and should not be modified or removed.

- index.html
- 404.html
- .nojekyll
