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
      if (this.items) this.loadTileSources()
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
        // if (this.items) this.viewer.open([{ url: this.items[0].url, type: 'image', buildPyramid: true }])

      })
    },
    async loadTileSources() {
      let manifestUrls = this.items.filter(item => item.manifest).map(item => item.manifest)
      let manifests = {}
      if (manifestUrls) {
        await Promise.all(manifestUrls.map(manifestUrl => fetch(manifestUrl).then(resp => resp.json())))
                     .then(manifestList => manifestList.forEach((manifest, idx) => manifests[manifestUrls[idx]] = manifest))
      }
      let tileSources = []
      this.items.forEach(item => {
        if (item.url) {
          tileSources.push({ tileSource: { url: item.url, type: 'image', buildPyramid: true }, opacity: 1 })
        } else if (item.manifest) {
          let manifest = manifests[item.manifest]
          let tileSource = `${manifest.sequences[0].canvases[manifest.seq || 0].images[0].resource.service['@id']}/info.json`
          tileSources.push({ tileSource, opacity: 1 })
        }
      })
      this.tileSources = tileSources
    }
  },     
  watch: {
    items: {
      handler: function (items) {
        if (items) this.loadTileSources()
      },
      immediate: false
    },
    active: {
      handler: function (isActive) { console.log(`${this.$options.name}.isActive=${isActive}`) },
      immediate: true
    },
    tileSources: {
      handler: function () {
        console.log(`${this.$options.name}.tileSources=${this.tileSources.length}`)      
        if (this.viewer) this.viewer.open(this.tileSources)
      },
      immediate: true
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
