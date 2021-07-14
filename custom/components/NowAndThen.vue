<template>
  <div id = "now-and-then">
    <div id = "para" v-html = "html"></div>
    <h3>Mode</h3>
    <button type = "button" :class="{'active': this.mode === 'curtain'}" class = "toggle-mode" id = "curtain-mode" @click = "initCurtain();">Curtain</button>
    <button type = "button" :class="{'active': this.mode === 'sync'}" class = "toggle-mode" id = "sync-mode" @click = "initSync();">Sync</button>
    <div id = "osd"></div>
  </div>
</template>

<script>

const dependencies = [
  'https://cdn.jsdelivr.net/npm/openseadragon@2.4/build/openseadragon/openseadragon.min.js',
  'https://cuberis.github.io/openseadragon-curtain-sync/src/openseadragon-curtain-sync.min.js'
]
const iiifService = 'https://iiif.juncture-digital.org'
const prefixUrl = 'https://openseadragon.github.io/openseadragon/images/'

module.exports = {
  name: 'NowAndThen',
  props: {
    html: {type: String, default: ''},
    params: {type: Array, default: () => ([])}
  },
  data: () => ({
    viewer: null,
    mode: 'curtain'
  }),
  computed: {
    compareItems() { return this.params.filter(param => param.viewer === 've-compare') },
  },
  mounted() { this.loadDependencies(dependencies, 0, this.init) },
  methods: {

    init() {
      this.initCurtain()
    },

    initSync() {
      this.mode = 'sync'
      this.loadImages().then(images => this.initViewer(images))
    },

    initCurtain() {
      this.mode = 'curtain'
      this.loadImages().then(images => this.initViewer(images))
    },

    initViewer(images) {
      console.log('initViewer')
      let main = document.getElementById('now-and-then')
      let container = document.getElementById('osd')
      if (container) {
        main.removeChild(container)
      }
      container = document.createElement('div')
      container.id = 'osd'
      container.style.height = '500px'
      main.appendChild(container)
      this.$nextTick(() => {
        this.viewer = new CurtainSyncViewer({
          mode: this.mode, // 'sync' or 'curtain'
          container,
          images,
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
    },

    async loadImages() {
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
      let manifests = await Promise.all(promises)
      manifests = manifests.map((manifest, idx) => {return {...manifest, ...this.compareItems[idx]}})
      let tileSources = manifests.map((manifest, idx) => {
        const opacity = idx === 0 ? 1 : this.mode === 'layers' ? 0 : 1
        const tileSource = manifest.sequences[0].canvases[manifest.seq || 0].images[0].resource.service
          ? `${manifest.sequences[0].canvases[manifest.seq || 0].images[0].resource.service['@id']}/info.json`
          : { url: manifest.sequences[0].canvases[manifest.seq || 0].images[0].resource['@id'] || manifest.metadata.find(md => md.label === 'source').value,
              type: 'image', buildPyramid: true }
        return tileSource
      })
      return tileSources.map((tileSource, idx) => { return { key: `item-${idx}`, tileSource, shown: true } })
    }
  
  },
  watch: {}
  }
</script>

<style>

#header {
  display: unset;
}
#now-and-then {
  padding: 58px 3% 0 3%;
}

#now-and-then > #para {
  padding: 0 0 2vh 0;
}

#osd {
  background-color: black;
  text-align: center;
}

.toggle-mode {
  font-size: 1.2em;
  padding: 0.6%;
  border-radius: 10px;
  color: white;
  background-color: #555;
  border: 2px solid #555;
  margin-bottom: 3vh;
}

.toggle-mode:hover {
  cursor: pointer;
  color: #555;
  background-color: #f6f6f6;
  border: 2px solid #04AA6D;
}

.active {
  border: 2px solid #04AA6D;
  background-color: #04AA6D;
}

</style>