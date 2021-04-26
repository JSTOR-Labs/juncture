<template>
  <div class="grid-container" :style="containerStyle">
    <div id="mynetwork" :style="networkStyle"></div>
    <div class="citation">
    <span class="title">{{this.items[0].title}}</span>
    </div>
  </div>
</template>

<script>
/* global vis, L */

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
    selected: String,
    width: Number,
    height: Number,
    hoverItemID: String,
    selectedItemID: String,
  },
  data: () => ({
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
        height: `${this.height}px`,
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
    },
    componentsBaseURL() {
      return window.location.hostname === "localhost"
        ? ""
        : "https://jstor-labs.github.io/visual-essays";
    },
  },
  mounted() {
    console.log(this.$options.name, this.items);
    // this.init();
    this.loadDependencies(dependencies, 0, this.init);
  },
  methods: {
    init() {
      var nodeslist = [];
      var edgeslist = [];
      console.log(this.items[0].url)
      //get input data here from file
      this.getInput(this.input)
        .then((delimitedDataString) => {
          const delimiter = this.input.split(".").pop() == "tsv" ? "\t" : ",";
          const data = this.transformData(
            this.delimitedStringToObjArray(delimitedDataString, delimiter)
          );
          nodeslist = data.nodes;
          edgeslist = data.edges;
        })
        .then((result) => this.getImages(nodeslist)) // eslint-disable-line no-unused-vars
        .then(() => {
          this.renderGraph(nodeslist, edgeslist);
        });
    },
    renderGraph(nodeslist, edgeslist) {
      let nodes = new vis.DataSet(nodeslist);
      let edges = new vis.DataSet(edgeslist);
      console.log("nodeslist", nodeslist);
      console.log("edgeslist", edgeslist);
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
          improvedLayout: true,
          clusterThreshold: 150,
          hierarchical: this.items[0].layout === "hierarchy" ? true : false,
        },
        edges: {
          arrows: this.items[0].arrows,
          //color: 'red',
          scaling: {
            label: true,
          },
          shadow: true,
          smooth: true,
        },
      };
      //init network
      var network = new vis.Network(container, data, options);
      network.on("click", (properties) => {
        var ids = properties.nodes;
        var clickedNodes = nodes.get(ids);
        console.log("clicked nodes:", clickedNodes);
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
          console.log('obj[nodeType].id', obj[nodeType].id, 'obj[nodeType].label', obj[nodeType].label);
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
            //let fixed = true
            nodes[nodeId] = id;
            if (label !== ""){
              transformed.nodes.push({ id, qid, label, title: label, x, y, physics, image, shape});
            }
          }
        });
      });
      objArray.forEach((obj) => {
        console.log('obj', obj);
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
    //get entity (image) for a single node
    getImage(node) {
      return this.getEntity(node.qid).then((result) => {
        node.label = result.labels.en ? result.labels.en.value : ''
        const imgSrc = result['summary info'] && result['summary info'].originalimage
          ? result['summary info'].originalimage.source
          : result.claims.image && result.claims.image.length > 0
            ? `https://commons.wikimedia.org/w/thumb.php?f=${result.claims.image[0].value}&w=140`
            : undefined
        if (imgSrc) {
          node.image = imgSrc;
          node.shape = "circularImage";
        }
        return node;
      });
    },
    getImages(nodeslist) {
      const promises = nodeslist
        .filter((node) => node.qid)
        .map((node) => this.getImage(node));
      return Promise.all(promises);
    },
    toQueryString(args) {
      const parts = [];
      Object.keys(args).forEach((key) => {
        parts.push(`${key}=${encodeURIComponent(args[key])}`);
      });
      return parts.join("&");
    },
    getEntity(eid) {
      let url = `https://visual-essays.app/entity/${encodeURIComponent(eid)}?refresh=false`;
      const args = {};
      if (this.context) args.context = this.context;
      //if (this.entity.article) args.article = this.entity.article
      if (Object.keys(args).length > 0) {
        url += `?${this.toQueryString(args)}`;
      }
      console.log(`getEntity=${url}`);
      return fetch(url).then((resp) => resp.json());
    },
    getSummaryInfo() {
      console.log("getSummaryInfo", this.eid, this.entity);
      if (
        this.entity["summary info"] === undefined &&
        !this.requested.has(this.entity.id)
      ) {
        this.requested.add(this.entity.id);
        this.getEntity().then((updated) => {
          if (!updated["summary info"]) {
            updated["summary info"] = null;
          }
          updated.id = this.eid;
          this.$store.dispatch("updateItem", updated);
        });
      }
    },
    addPositions(){

    }
    //adding function for now
    delimitedStringToObjArray(delimitedData, delimiter) {
      delimiter = delimiter || `\t`;
      const objArray = [];
      const lines = delimitedData.split("\n").filter(line => line.trim() !== "");
      if (lines.length > 1) {
        const keys = lines[0].split(delimiter).map(key => key.trim());
        lines.slice(1).forEach(line => {
          let obj = {};
          line
            .split(delimiter)
            .map(value => value.trim())
            .forEach((value, i) => {
              let rawKey = keys[i].split(".");
              let key = rawKey[0];
              let prop = rawKey.length === 2 ? rawKey[1] : "id";
              if (!obj[key]) obj[key] = {};
              if (value || prop === "id") {
                obj[key][prop] = value;
              }
            });
          objArray.push(obj);
        });
        let assignedId = 0;
        let labels = {};
        objArray.forEach(obj => {
          Object.values(obj).forEach(child => {
            if (child.id === "" && child.label) {
              if (!labels[child.label]) labels[child.label] = ++assignedId;
              child.id = labels[child.label];
            }
          });
        });
      }
      return objArray;
    }
  },
  watch: {
    items() {
      console.log(`${this.$options.name}.watch.items`, this.items)
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

  .citation {
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
