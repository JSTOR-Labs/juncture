<template>
  <div id="map">
    test
  </div>
</template>

<script>


const dependencies = [
  'https://cdn.jsdelivr.net/npm/leaflet@1.5.1/dist/leaflet.css',
  'https://cdn.jsdelivr.net/npm/leaflet@1.5.1/dist/leaflet.js'
]

module.exports = {
  name: 'Map',
  props: {
    locations: {type: Array, default: () => ([])}
  },
  data: () => ({
    map: null
  }),
  computed: {
    locationsWithCoords() { 
      return this.locations
        .filter(loc => loc.metadata && loc.metadata.coords)
        .map(loc => {
          if (!Array.isArray(loc.metadata.coords))
            loc.metadata.coords = loc.metadata.coords.split(',').map(coord => parseFloat(coord))
          return loc
        })
    }
  },
  mounted() { this.loadDependencies(dependencies, 0, this.init) },
  methods: {

    init() {
      this.createMap()
      this.addMarkers()
    },

    createMap() {
      this.map = L.map('map', {
        center: [51.2119, 0.79756], 
        zoom: 10, 
        layers: [
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', 
                      { maxZoom: 18, attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' })
        ]
      })
    },

    addMarkers() {
      this.locationsWithCoords.forEach(loc => {
        L.marker(loc.metadata.coords).addTo(this.map).bindPopup(loc.heading)
      })
    }

  },
  watch: {}
}

</script>

<style>

  #map {
    height: 100%;
  }

</style>