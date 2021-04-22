<template>
    <div id="map" :style="containerStyle"></div>
</template>

<script>

const label = 'Map Viewer'
const icon = 'fas fa-map-marker-alt'
const dependencies = [
  'https://cdn.jsdelivr.net/npm/leaflet@1.5.1/dist/leaflet.css',
  'https://cdn.jsdelivr.net/npm/leaflet@1.5.1/dist/leaflet.js'
]

// A leaflet baselayer
const baseLayers = {
  'OpenStreetMap': [
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    { maxZoom: 18, attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' }
  ]
}

const defaults = {
  // Leaflet Map options
  basemap: 'OpenStreetMap',
  center: [25, 0],
  zoom: 2.5,
  maxZoom: 16
}

module.exports = {
  name: 've-map',
  props: {
    items: { type: Array, default: () => ([]) },
    allItems: { type: Array, default: () => ([]) },
    entities: { type: Object, default: () => ({}) },
    active: Boolean
  },
  data: () => ({
    label,
    icon,
    dependencies,
    map: null,
    tileLayers: [],
  }),
  computed: {
    mapDef() { return this.items.find(item => item.viewer === this.$options.name) },
    basemap() { return this.mapDef.basemap || defaults.basemap },
    center() { 
      let coordsStr = this.entities[this.mapDef.center] ? this.entities[this.mapDef.center].coords : this.mapDef.center
      return coordsStr ? coordsStr.split(',').map(coord => parseFloat(coord)) : defaults.center 
    },
    zoom() { return this.mapDef.zoom || defaults.zoom },
    maxZoom() { return this.mapDef['max-zoom'] || defaults.maxZoom },

    mapStyle() { return {
      width: `${this.width}px`,
      height: this.active ? '100%' : '0',
      overflowY: 'auto !important',
      marginLeft: '0' }
    },
    containerStyle() { return {
      width: `${this.width}px`,
      height: this.active ? '100%' : '0' }
    }
  },
  mounted() { this.loadDependencies(this.dependencies, 0, this.init) },
  methods: {
    init() {
      console.log(this.$options.name, this.mapDef)
      if (this.active) this.createMap()
    },
    createMap(reload) {
      if (reload && this.map) {
        this.map.off()
        this.map.remove()
        this.map = null
      }
      if (!this.map) {
        this.$nextTick(() => {
          console.log('createMap', document.getElementById('map').clientHeight)
          this.map = L.map('map', {
            center: this.center, 
            zoom: this.zoom, 
            maxZoom: this.maxZoom, 
            layers: [L.tileLayer(...baseLayers.OpenStreetMap)]
          })
        })
      }
    }
  },
  watch: {
    active: {
      handler: function () { 
        console.log(`${this.$options.name}.active=${this.active}`) 
        if (this.active && !this.map) this.createMap()
      },
      immediate: false
    },
    mapDef: {
      handler: function (mapDef) {
        console.log('mapDef', mapDef)
        if (this.map) {
          this.map.flyTo(this.center, this.zoom)
        } else {
          this.createMap()
        }
      },
      immediate: false
    }
  }
}
</script>

<style>

  .map-viewer {
    display: grid;
    grid-template-columns: auto;
    grid-template-rows: 1fr auto;
    grid-template-areas:
    "map-main";
    height: 100%;
  }

  #map {
    grid-area: map-main;
  }

  .map-label {
    /* row-start / column-start / row-end / column-end */
    grid-area: mapcite;
    z-index: 2;
    justify-self: stretch;
    align-self: stretch;
    /* background-color: rgba(255, 255, 255, 0.8); */
    background-color: #ccc;
    padding: 3px 6px;
      text-align: center;
      line-height: 1;
  }

  .title {
    font-size: 0.9rem;
    font-weight: bold;
  }

</style>