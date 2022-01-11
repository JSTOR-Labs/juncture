<template>
  <div id="main" :style="containerStyle">
    <div id="osd"></div>
  </div>
</template>

<script>

// https://cuberis.github.io/openseadragon-curtain-sync/

const iiifService = 'https://iiif.juncture-digital.org'
const prefixUrl = 'https://openseadragon.github.io/openseadragon/images/'

module.exports = {
  name: 've-compare',
  props: {
    items: { type: Array, default: () => ([]) },
    viewerIsActive: Boolean
  },
  data: () => ({
    viewerLabel: 'Image Compare',
    viewerIcon: 'fas fa-images',
    dependencies: [
      'https://cdn.jsdelivr.net/npm/openseadragon@2.4/build/openseadragon/openseadragon.min.js',
      'https://jstor-labs.github.io/juncture/js/openseadragon-curtain-sync.min.js'
    ],
    tileSources: [],
    viewer: null
  }),
  computed: {
    containerStyle() { return { height: this.viewerIsActive ? '100%' : '0' } },
    compareItems() { return this.items.filter(item => item[this.$options.name]) },
    mode() { let itemsWithMode = this.compareItems.filter(item => item.sync || item.curtain).map(item => item.sync ? 'sync' : 'curtain') 
             return itemsWithMode.length > 0 ? itemsWithMode[0] : 'curtain'
    },
    images() { return this.tileSources.map((tileSource, idx) => { 
      return { key: `item-${idx}`, tileSource, shown: true } 
      })
    }
  },
  mounted() { this.loadDependencies(this.dependencies, 0, this.init) },
  methods: {
    init() { this.loadManifests() },
    initViewer() {
      if (this.viewerIsActive) {
      let main = document.getElementById('main')
      let container = document.getElementById('osd')
      if (container) {
        main.removeChild(container)
      }
      container = document.createElement('div')
      container.id = 'osd'
      container.style.height = '100%'
      main.appendChild(container)
      this.$nextTick(() => {
        this.viewer = new CurtainSyncViewer({
          mode: this.mode, // 'sync' or 'curtain'
          container,
          images: this.images,
          osdOptions: { // OpenSeaDragon options
            autoHideControls: false,
            showHomeControl: true,
            showZoomControl: true,
            homeFillsViewer: false,
            prefixUrl,
            zoomPerClick: 2,
            visibilityRatio: 1,
            wrapHorizontal: false,
            constrainDuringPan: true,
            minZoomImageRatio: 1.35,  
            // maxZoomPixelRatio: Infinity,
            maxZoomPixelRatio: 3,
            viewportMargins: {left:0, top:0, bottom:0, right:0}
          }
        })
      })
      }
    },
    loadManifests() {
      let promises = this.compareItems.map(item => {
        if (item.manifest) {
          return fetch(item.manifest).then(resp => resp.json())
        } else if (item.url) {
          let data = {};
          ['url', 'label', 'description', 'attribution', 'license'].forEach(field => {
            if (item[field]) data[field] = item[field]
          })
          return fetch(`${iiifService}/manifest/`, {
            method: 'POST',
            headers: {'Content-type': 'application/json'},
            body: JSON.stringify(data)
          }).then(resp => resp.json())
        }
      })
      Promise.all(promises).then(manifests => {
          this.manifests = manifests.map((manifest, idx) => {return {...manifest, ...this.compareItems[idx]}})
          this.tileSources = this.manifests.map((manifest, idx) => {
            const opacity = idx === 0 ? 1 : this.mode === 'layers' ? 0 : 1
            const tileSource = manifest.sequences[0].canvases[manifest.seq || 0].images[0].resource.service
              ? `${manifest.sequences[0].canvases[manifest.seq || 0].images[0].resource.service['@id']}/info.json`
              : { url: manifest.sequences[0].canvases[manifest.seq || 0].images[0].resource['@id'] || manifest.metadata.find(md => md.label === 'source').value,
                 type: 'image', buildPyramid: true }
            return tileSource
          })
        })
    }
  },     
  watch: {
    compareItems() { this.loadManifests() },
    images() { this.initViewer() },
    active() { this.initViewer() }
  }
}

</script>

<style>
</style>
