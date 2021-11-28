<template>
  <div id="map" style="height:100%;padding-bottom:400px;"></div>
</template>

<script>

const dependencies = [
  'https://cdn.jsdelivr.net/npm/leaflet@1.5.1/dist/leaflet.css',
  'https://cdn.jsdelivr.net/npm/leaflet@1.5.1/dist/leaflet.js'
]

module.exports = {  
  name: 'custom-main',
  props: {
    html: { type: String, default: '' },
    entities: { type: Object, default: () => ({}) },
    params: { type: Array, default: () => ([]) },
  },
  data: () => ({
    map: null
  }),
  computed: {
    entitiesWithCoords() { return Object.values(this.entities).filter(entity => entity.coords) },
    entitiesWithGeojson() { return Object.values(this.entities).filter(entity => entity.geojson) }
  },
  mounted() {this.loadDependencies(dependencies, 0, this.init)},
  methods: {
    init() {
      // console.log(this.params, this.entities, this.entitiesWithCoords, this.entitiesWithGeojson)
      this.createMap()
    },
    createMap() {
      this.map = L.map('map', {
        center: [25, 0], 
        zoom: 2.5, 
        layers: [
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', 
                      { maxZoom: 18, attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' })
        ]
      })
    }
  },
  watch: {}
}

</script>

<style>
</style>