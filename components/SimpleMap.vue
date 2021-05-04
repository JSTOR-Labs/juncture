<template>
    <div id="map" :style="containerStyle"></div>
</template>

<script>

const viewerLabel = 'Map Viewer'
const viewerIcon = 'fas fa-map-marker-alt'
const dependencies = [
  'https://cdn.jsdelivr.net/npm/leaflet@1.5.1/dist/leaflet.css',
  'https://cdn.jsdelivr.net/npm/leaflet@1.5.1/dist/leaflet.js',
  'https://gitcdn.link/repo/pa7/heatmap.js/develop/build/heatmap.min.js',
  'https://gitcdn.link/repo/pa7/heatmap.js/develop/plugins/leaflet-heatmap/leaflet-heatmap.js'
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
  name: 've-simple-map',
  props: {
    items: { type: Array, default: () => ([]) },
    allItems: { type: Array, default: () => ([]) },
    entities: { type: Object, default: () => ({}) },
    active: Boolean
  },
  data: () => ({
    viewerLabel,
    viewerIcon,
    dependencies,
    map: null,
    tileLayers: [],
  }),
  computed: {
    mapDef() { return this.items.find(item => item.viewer === this.$options.name) || {} },
    basemap() { return this.mapDef.basemap || defaults.basemap },
    center() { 
      let coordsStr = this.entities[this.mapDef.center] ? this.entities[this.mapDef.center].coords : this.mapDef.center
      return coordsStr ? coordsStr.split(',').map(coord => parseFloat(coord)) : defaults.center 
    },
    zoom() { return this.mapDef.zoom || defaults.zoom },
    maxZoom() { return this.mapDef['max-zoom'] || defaults.maxZoom },
    layers() { return this.items.filter(item => item['ve-map-layer']) },

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
          this.layers.forEach(layer => {
            if (layer.heatmap) this.addHeatmap(layer)
          })
        })
      }
    },
    addHeatmap(layer) {
      let cfg = {
        // radius should be small ONLY if scaleRadius is true (or small radius is intended)
        // if scaleRadius is false it will be the constant radius used in pixels
        radius: 2,
        maxOpacity: .8,
        // scales the radius based on map zoom
        scaleRadius: true,
        // if set to false the heatmap uses the global maximum for colorization
        // if activated: uses the data maximum within the current map boundaries
        //   (there will always be a red spot with useLocalExtremas true)
        useLocalExtrema: true,
        // which field name in your data represents the latitude - default "lat"
        latField: 'lat',
        // which field name in your data represents the longitude - default "lng"
        lngField: 'lng',
        // which field name in your data represents the data value - default "value"
        valueField: 'count'
      }
      let heatmapLayer = new HeatmapOverlay(cfg)
      this.map.addLayer(heatmapLayer)

      fetch(layer.url).then(resp => resp.text())
        .then(delimitedDataString => {
          let byPlace = {}
          this.delimitedStringToObjArray(delimitedDataString)
            .forEach(item => {
              if (!byPlace[item.PlaceQID.id]) byPlace[item.PlaceQID.id] = {lat: parseFloat(item.Lat1.id), lng: parseFloat(item.Long1.id), count: 0}
              byPlace[item.PlaceQID.id].count += 1
            })
          let heatmapData = {max: 8, data: Object.values(byPlace)}
          heatmapLayer.setData(heatmapData)
        })
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
    },
    items: {
      handler: function (items) {
        console.log('items', items)
      },
      immediate: true
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