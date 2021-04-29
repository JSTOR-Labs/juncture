<a href="https://visual-essays.app"><img src="https://gitcdn.link/repo/jstor-labs/juncture/main/images/ve-button.png"></a>

<param ve-config
       title="Video examples"
       banner="https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/WorldMap-A_with_Frame.png/1024px-WorldMap-A_with_Frame.png"
       layout="vtl"
       author="JSTOR Labs team">

## Introduction
The video viewer is used to associate and display a video with a text element. Youtube videos are supported in the current version of the visual essay tool. Other streaming services may be added in future versions.
The basic tag for video requires an `id` attribute for the URL of the video. 
```html
<param ve-video id="5upF4rJUxC4">
```
<param ve-video id="5upF4rJUxC4">

### Options
The video tag accepts an optional `title` attribute and `start` attribute.
```html
<param ve-video
	vid="C0CIRCjoICA"
	title="Sylbo, The Last Speakers of the Lost Whistling Language.">
```
<param ve-video
	vid="C0CIRCjoICA"
	title="Sylbo, The Last Speakers of the Lost Whistling Language.">
