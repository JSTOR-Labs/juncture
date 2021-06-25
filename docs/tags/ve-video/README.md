<param ve-config title="Documentation" component="default" class="documentation" fixed-header>

<param ve-config title="Documentation" component="default" class="documentation" fixed-header>

# Video viewer

## Overview
![Video Viewer](video.png){: .right .dropshadow .border .thumb-300w} 
The video viewer is used to associate and display a video with a text element.  Youtube videos are supported in the current version of the visual essay tool.  Other streaming services may be added in future versions.

## Syntax
```html
<param ve-video>
```

## Options
- __id__:  The Youtube video ID.
- __title__:  The title attribute is used for the image caption.  Markdown text formatting is supported in the title allowing for italicized and bold text.
- __start__:  The starting timestamp (in seconds).  If not provided the video will start playing from the beginning.

## Usage examples

```html
<param ve-video id="5upF4rJUxC4" title="NYBG 2019 Corpse Flower Timelapse">
```
