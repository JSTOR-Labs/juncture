<template>
  <div class="grid-container" :style="containerStyle">
    <div id="mynetwork" :style="networkStyle"></div>
    <div class="footerBar">
    <span class="title">{{this.items[0].title}}</span>
    </div>
  </div>
</template>

<script>
/* global vis, L */
const viewerLabel = "Network Viewer"
const viewerIcon = "fas fa-project-diagram"
const dependencies = [
  "https://unpkg.com/vis-network/styles/vis-network.min.css",
  "https://unpkg.com/vis-data@latest/peer/umd/vis-data.min.js",
  "https://unpkg.com/vis-network@latest/peer/umd/vis-network.min.js",
];
const defaults = {
  popupOptions: { autoClose: false, closeButton: false, closeOnClick: false },
};
module.exports = {
  name: "ve-vis-network",
  props: {
    items: { type: Array, default: () => [] },
    viewerIsActive: Boolean,
    selected: String,
    width: Number,
    height: Number,
    hoverItemID: String,
    selectedItemID: String,
  },
  data: () => ({
    viewerLabel,
    viewerIcon,
    activeWindow: undefined,
    popups: {},
    active: new Set(),
  }),
  computed: {
    networkStyle() {
            return {
                width: `${this.width}px`,
                //height: `${this.height}px`,
                overflowY: 'auto !important',
                marginLeft: '0',   
            }
    },
    containerStyle() {
      return {
        width: `${this.width}px`,
        height: this.viewerIsActive ? `${this.height}px` : '0',
        overflowY: "auto !important",
        backgroundColor: this.items[0] ? this.items[0].background || 'white' : 'white',
      };
    },
    activeElements() {
      return this.$store.getters.activeElements;
    },
    entities() {
      return this.itemsInActiveElements.filter((item) => item.tag === "entity");
    },
    itemsInActiveElements() {
      return this.$store.getters.itemsInActiveElements;
    },
    apiBaseURL() {
      return window.location.origin;
    },
    input() { 
      return this.items[0] && this.items[0].file || this.items[0].url
    }
  },
  mounted() {
    this.loadDependencies(dependencies, 0, this.init);
  },
  methods: {
    init() {
      var nodeslist = []
      var edgeslist = []
      //get input data here from file
      this.getInput(this.input)
        .then((delimitedDataString) => {
          const delimiter = this.input.split(".").pop() == "tsv" ? "\t" : ",";
          const data = this.transformData(
            this.delimitedStringToObjArray(delimitedDataString, delimiter)
          )
          edgeslist = data.edges
          return this.getImages(data.nodes)
        })
        .then(nodesWithImages => nodeslist = nodesWithImages)
        .then(() => this.renderGraph(nodeslist, edgeslist))
    },
    renderGraph(nodeslist, edgeslist) {
      let nodes = new vis.DataSet(nodeslist);
      let edges = new vis.DataSet(edgeslist);
      var container = document.getElementById("mynetwork");
      var data = {
        nodes: nodes,
        edges: edges,
      };
      let options = {
        interaction: { hover: true },
        physics:{
           stabilization: false,
       },
        layout: {
          randomSeed: undefined,
          improvedLayout: false,
          clusterThreshold: 250,
          hierarchical: this.items[0].layout === "hierarchy" ? true : false,
        },
        edges: {
          arrows: this.items[0].arrows || 'to',
          //color: 'red',
          scaling: {
            label: true,
          },
          shadow: true,
          smooth: true,
          length: 300,
        },
      };
      //init network
      var network = new vis.Network(container, data, options);
      network.on("click", (properties) => {
        var ids = properties.nodes;
        var clickedNodes = nodes.get(ids);
        if (clickedNodes.length > 0) {
          this.setSelectedItemID(clickedNodes[0].qid);
        }
      });
      network.body.emitter.emit("_dataChanged");
      network.redraw();
    },
    setHoverItemID(itemID) {
      this.$emit("hover-id", itemID);
    },
    setSelectedItemID(itemID) {
      this.$emit("selected-id", itemID);
    },
    addEventHandlers(elem, itemId) {
      elem.on("click", () => {
        this.setSelectedItemID(itemId);
      });
      elem.on("mouseover", () => {
        this.setHoverItemID(itemId);
      });
      elem.on("mouseout", () => {
        this.setHoverItemID();
      });
    },
    addPopup(id, label, latLng, offset) {
      if (!this.popups[id]) {
        const popup = L.popup({
          ...defaults.popupOptions,
          ...{ offset: L.point(0, offset || 0) },
        });
        popup.setLatLng(latLng);
        popup.setContent(`<h1 data-eid="${id}">${label}</h1>`);
        popup.options.id = id;
        this.popups[id] = popup;
      }
    },
    getInput() {
      return fetch(this.input).then((resp) => resp.text());
    },
    transformData(objArray) {
      const nodes = {};
      const transformed = { nodes: [], edges: [] };
      objArray.forEach((obj) => {
        ['source', 'target'].forEach((nodeType) => {
          let nodeId = obj[nodeType].id || obj[nodeType].label;
          if (nodes[nodeId] === undefined) {
            let id = `${transformed.nodes.length}`;
            let qid =
              obj[nodeType].id[0] === "Q" ? obj[nodeType].id : undefined;
            let label = obj[nodeType].label || obj[nodeType].id;
            let x = obj[nodeType].x ? (this.width)*(obj[nodeType].x/100) : undefined;
            let y = obj[nodeType].y ? (this.height)*(obj[nodeType].y/100) : undefined;
            let physics = obj[nodeType].x && obj[nodeType].y ? false : true;
            let image = obj[nodeType].image ? obj[nodeType].image : undefined;
            let shape = obj[nodeType].image ? "circularImage" : undefined;
            let title = obj[nodeType].label || obj[nodeType].id;
            
            var element = document.createElement("div");
            element.className = 'node'+id;
            if (obj[nodeType].html){
              element.innerHTML = obj[nodeType].html;
              title = element;
            }
            
            nodes[nodeId] = id;
            if (label !== ""){
              transformed.nodes.push({ id, qid, label, title: title, x, y, physics, image, shape });
            }
          }
        });
      });
      objArray.forEach((obj) => {
        if (obj.target.id !== ""){
          transformed.edges.push({
            from: nodes[obj.source.id || obj.source.label],
            to: nodes[obj.target.id || obj.target.label],
            title: obj.edge ? (obj.edge.label || obj.edge.id) : ''
          });
        }
        
      });
      return transformed;
    },
    async getImages(nodeslist) {
      let eids = nodeslist.filter(node => node.qid).map(node => node.qid)
      let entities = await this.getEntityData(eids)
      return nodeslist.map(node => {
        if (node.qid) {
          node.image = entities[node.qid].thumbnails[0]
          node.shape = 'circularImage'
        }
        return node
      })
    },
  
    // Gets labels and images for referenced Wikdata entities
    async getEntityData(eids) {
      let values = Array.from(eids).map(eid => `(<http://www.wikidata.org/entity/${eid}>)`).join(' ')
      let query = `SELECT ?item ?label ?images WHERE {
                      VALUES (?item) { ${values} }
                      ?item rdfs:label ?label . FILTER(LANG(?label) = 'en')
                      OPTIONAL { ?item wdt:P18 ?images . }
                    }`
      let resp = await fetch('https://query.wikidata.org/sparql', {
        method: 'POST', body: `query=${encodeURIComponent(query)}`, 
        headers: { Accept: 'application/sparql-results+json', 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      resp = await resp.json()
      let entities = {}
      resp.results.bindings.forEach(rec => {
        let eid = rec.item.value.split('/').pop()
        if (!entities[eid]) entities[eid] = {eid, label: rec.label.value, images: [], thumbnails: []}
        if (rec.images && entities[eid].images.indexOf(rec.images.value) < 0) {
          entities[eid].images.push(rec.images.value)
          entities[eid].thumbnails.push(this.commonsImageUrl(rec.images.value, 200))
        }
      })
      return entities
    },
    commonsImageUrl(url, width) {
      // Converts Wikimedia commons File URL to an image link
      //  If a width is provided a thumbnail is returned
      let mwImg = url.indexOf('Special:FilePath') > 0 ? url.split('/Special:FilePath/').pop() :  url.split('/File:').pop()
      mwImg = decodeURIComponent(mwImg).replace(/ /g,'_')
      const ImgMD5 = md5(mwImg)
      const extension = mwImg.slice(mwImg.length-4)
      let imgUrl = `https://upload.wikimedia.org/wikipedia/commons/${width ? 'thumb/' : ''}`
      imgUrl += `${ImgMD5.slice(0,1)}/${ImgMD5.slice(0,2)}/${mwImg}`
      if (width) imgUrl += `/${width}px-${mwImg}`
      if (extension === '.svg') imgUrl += '.png'
      if (extension === '.tif') imgUrl += '.jpg'
      return imgUrl
    }
    
  },
  watch: {
    items() {
      this.init()
    }
  }
};
</script>

<style>
  .vis-network {
    overflow: visible;
  }
  #vis,
  .grid-container {
        display: grid;
        grid-template-rows: 1fr auto;
        grid-template-areas:
        "main"
        "footer";
    }
  .footerBar {
      /* row-start / column-start / row-end / column-end */
      grid-area: footer;
      z-index: 2;
      justify-self: stretch;
      align-self: stretch;
      /* background-color: rgba(255, 255, 255, 0.8); */
      background-color: #ccc;
      padding: 9px 6px;
        text-align: center;
        line-height: 1;
    }
  #mynetwork {
    /*width: 100%;
    height: 100%;
    */
    grid-area: main
  }
  #networktitle {
    z-index:100;
    right: 0;
    bottom: 0;
    width: 100%;
    font: 1.0em;
    background-color:rgba(143, 223, 255, 0.5);
    padding: 2%;
    color: black;
    text-align: center;
  }
  .title {
      font-size: 0.9rem;
      font-weight: bold;
    }
</style>
