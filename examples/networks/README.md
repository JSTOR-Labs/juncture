<a href="https://juncture-digital.org"><img src="https://gitcdn.link/repo/jstor-labs/juncture/main/images/ve-button.png"></a>

<param ve-config
       title="Network examples"
       banner="https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/WorldMap-A_with_Frame.png/1024px-WorldMap-A_with_Frame.png"
       layout="vtl"
       author="JSTOR Labs team">

<a class="nav" href="/examples"><i class="fas fa-arrow-circle-left"></i>Back to examples</a>

## Introduction

This sample essay provides examples of different netowork graphs that can be incorporated into an essay.  There are 3 variations of networks currently supported:
* [D3Plus Basic Network](#d3plussimple)
* [D3Plus Ring Network](#d3plusring)
* [Vis.js Network](#visjs)

## D3Plus Basic Network
This tag renders a basic network diagram using the D3Plus library. D3plus is a JavaScript re-usable chart library that extends the popular D3.js to enable the easy creation of visualizations.  Example diagrams can be seen at [https://d3plus.org/examples/](https://d3plus.org/examples/).  Documentation is available at [https://d3plus.org/docs/](https://d3plus.org/docs/). The `ve-d3plus-network` tag is used to generate this diagram and currently supports comma separated (CSV) or tab separated (TSV) delimited text files as input data. This tag should include the `url` attribute to point to the data file.
```markdown
<param ve-d3plus-network url="https://jstor-labs.github.io/ve-components/public/data/medici.tsv">
```
<param ve-d3plus-network url="https://jstor-labs.github.io/ve-components/public/data/medici.tsv">


## D3Plus Ring Network
This ring network diagram uses the D3Plus library. Rings are a way to view network connections focused on 1 node in the network.  This visualization shows primary and secondary connections of a specific node, and allows the user to click on a node to recenter the visualization on that selected node. The `ve-d3plus-ring` tag is used to generate this diagram and currently supports comma separated (CSV) or tab separated (TSV) delimited text files as input data. The `url` attribute is required to point to the data file. It also uses an optional `center` attribute to identify the name of the network'ss central node.
```html
<param ve-d3plus-ring-network 
       url="https://jstor-labs.github.io/ve-components/public/data/medici.tsv"
       center="Anna Maria Luisa de' Medici">
```
<param ve-d3plus-ring-network 
       url="https://raw.githubusercontent.com/JSTOR-Labs/plant-humanities/develop/data/heliconia_network_interactions.tsv"
       center="Heliconia imbricata">
       
## Vis.js Network
This network diagram is rendered using the Vis.js library, a dynamic, browser based visualization JavaScript library. Examples of network graphs created in Vis.js can be seen at [https://visjs.github.io/vis-network/examples/](https://visjs.github.io/vis-network/examples/). The documentation for networks can be viewed at [https://visjs.github.io/vis-network/docs/network/](https://visjs.github.io/vis-network/docs/network/). The `ve-vis-network` tag is used to generate this graph and currently supports comma separated (CSV) or tab separated (TSV) delimited text files as input data. The `url` attribute is required to point to the data file. An optional `title` attribute can be defined to give the network graph a title. 
```html
<param ve-vis-network title="Anna Maria Luisa de Medici's Network" url="https://jstor-labs.github.io/plant-humanities/graphs/peony_medici.tsv">
```
<param ve-vis-network title="Anna Maria Luisa de Medici's Network" url="https://jstor-labs.github.io/plant-humanities/graphs/peony_medici.tsv">
