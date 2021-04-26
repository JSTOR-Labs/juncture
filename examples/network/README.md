<a href="https://juncture-digital.org"><img src="https://raw.githubusercontent.com/jstor-labs/juncture/main/images/ve-button.png"></a>

<param ve-config
       title="Network examples"
       banner="https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/WorldMap-A_with_Frame.png/1024px-WorldMap-A_with_Frame.png"
       layout="vtl"
       author="JSTOR Labs team">

## Introduction

This sample essay provides examples of different netowork graphs that can be incorporated into an essay.  There are 3 variations of networks currently supported:
* [D3Plus Simple Network](#d3plussimple)
* [D3Plus Ring Network](#d3plusring)
* [Vis.js Network](#visjs)


```markdown
<param ve-d3plus-network url="https://jstor-labs.github.io/ve-components/public/data/medici.tsv">
```

```html
<param ve-d3plus-ring-network 
       url="https://jstor-labs.github.io/ve-components/public/data/medici.tsv"
       center="Anna Maria Luisa de' Medici">
```

```html
<param ve-vis-network title="Heliconia imbricata and hummingbird mutualistic interactions" url="https://jstor-labs.github.io/plant-humanities/graphs/heliconia-v3.tsv">
```
