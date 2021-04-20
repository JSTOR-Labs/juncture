<template>
  <div class="osd" id="osd" :style="containerStyle"></div>
</template>

<script>
/* global OpenSeadragon */

const label = 'Image Viewer'
const icon = 'far fa-file-image'
const dependencies= [
  'https://cdn.jsdelivr.net/npm/openseadragon@2.4/build/openseadragon/openseadragon.min.js'
]
const prefixUrl = 'https://openseadragon.github.io/openseadragon/images/'

module.exports = {
  name: 've-image',
  props: {
    items: Array,
    active: Boolean
  },
  data: () => ({
    label,
    icon,
    dependencies,
    osdElem: null,
    tileSources: []
  }),
  computed: {
    containerStyle() { return { height: this.active ? '100%' : '0' } }
  },
  mounted() { this.loadDependencies(this.dependencies, 0, this.init) },
  methods: {
    init() {
      console.log(this.$options.name, this.items)
      this.osdElem = document.getElementById('osd')
      this.initViewer()
    },
    initViewer() {
      if (this.viewer) {
        this.viewer.destroy()
      }
      this.$nextTick(() => {
        let options = {
          id: 'osd',
          prefixUrl,
          // toolbar:        'osd-toolbar',
          zoomInButton:   'zoom-in',
          zoomOutButton:  'zoom-out',
          homeButton:     'go-home',
          // infoButton: 'info-box',
          // fullPageButton: 'full-page',
          // nextButton:     'next',
          // previousButton: 'previous',
          visibilityRatio: 1.0,
          constrainDuringPan: true,
          // minZoomImageRatio: 0, 
          minZoomImageRatio: 0.6,
          // maxZoomPixelRatio: Infinity,
          maxZoomPixelRatio: 10,
          homeFillsViewer: true,
          viewportMargins: {left:0, top:0, bottom:0, right:0},
          sequenceMode: true,
          showReferenceStrip: true,
          showNavigationControl: true,
          showHomeControl: true,
          showZoomControl: true,
          showFullPageControl: false,
          showSequenceControl: false,
          showNavigator: false
        }
        this.viewer = OpenSeadragon(options)
        if (this.items) this.viewer.open([{ url: this.items[0].url, type: 'image', buildPyramid: true }])

      })
    },
    loadTileSources() {
      console.log('loadTileSources')
      let tileSources = []
      let manifests = []
      this.items.forEach(item => {
        if (item.url) {
          tileSources.push({ tileSource: { url: items.url, type: 'image', buildPyramid: true }, opacity: 1 })
        } else if (item.manifest) {
          tileSources.push({ tileSource: null, opacity: 1 })
          manifests.push(item.manifest)
        }
      })
      if (manifests.length > 0) this.loadManifests(manifests)
      this.tileSources = tileSources
    },
    loadManifests(manifests) {
      console.log('loadManifests', manifests)
    }
  },     
  watch: {
    items: {
      handler: function (items) {
        this.loadTileSources()
        console.log('OpenSeadragonViewer.watch.items', items)
        this.viewer.open([{ url: items[0].url, type: 'image', buildPyramid: true }])
      },
      immediate: false
    },
    active: {
      handler: function (isActive) { console.log(`${this.$options.name}.active=${isActive}`) },
      immediate: true
    },
    tileSources() {
      console.log(`${this.$options.name}.tileSources=${this.tileSources.length}`)      
      this.viewer.open(this.tileSources)
    }
  }
}
</script>

<style scoped>

  .osd {
    width: 100%;
    height: 100%;
    background: gray;
  }

</style>
