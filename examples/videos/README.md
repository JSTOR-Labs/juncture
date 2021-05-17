<a href="https://juncture-digital.org"><img src="https://gitcdn.link/repo/jstor-labs/juncture/main/images/ve-button.png"></a>

<param ve-config
       title="Video examples"
       banner="https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/WorldMap-A_with_Frame.png/1024px-WorldMap-A_with_Frame.png"
       layout="vtl"
       author="JSTOR Labs team">

<a class="nav" href="/examples"><i class="fas fa-arrow-circle-left"></i>Back to examples</a>

## Introduction
The video viewer is used to associate and display a video with a text element. Youtube videos are supported in the current version of the visual essay tool. Other streaming services may be added in future versions.
The basic tag for video requires an `id` attribute for the URL of the video. 
```html
<param ve-video id="https://www.youtube.com/embed/_VwKvS6QpsI">
```
<param ve-video id="https://www.youtube.com/embed/_VwKvS6QpsI">

### Options
The video tag accepts an optional `title` attribute and `start` attribute.
```html
<param ve-video
	id="https://www.youtube.com/embed/C0CIRCjoICA"
	title="Sylbo, The Last Speakers of the Lost Whistling Language.">
```
<param ve-video
	id="https://www.youtube.com/embed/C0CIRCjoICA"
	title="Sylbo, The Last Speakers of the Lost Whistling Language.">
	
### Vimeo
The video tag supports videos from Vimeo and YouTube.
```html
<param ve-video
	id="https://player.vimeo.com/video/76979871?loop=false&amp;byline=false&amp;portrait=false&amp;title=false&amp;speed=true&amp;transparent=0&amp;gesture=media"
	>
```
<param ve-video
	id="https://player.vimeo.com/video/76979871?loop=false&amp;byline=false&amp;portrait=false&amp;title=false&amp;speed=true&amp;transparent=0&amp;gesture=media"
	>
