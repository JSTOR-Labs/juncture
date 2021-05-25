<template>
  <div class="osd" id="osd" :style="containerStyle"></div>
</template>

<script>
/* global OpenSeadragon */

module.exports = {
  name: 've-simple-image',
  props: {
    items: Array,
    viewerIsActive: Boolean
  },
  data: () => ({
    viewerLabel: 'Simple Image Viewer',
    viewerIcon: 'far fa-file-image',
    dependencies: ['https://cdn.jsdelivr.net/npm/openseadragon@2.4/build/openseadragon/openseadragon.min.js'],
    viewer: null,
    tileSources: []
  }),
  computed: {
    containerStyle() { return { height: this.viewerIsActive ? '100%' : '0' } }
  },
  mounted() { this.loadDependencies(this.dependencies, 0, this.init) },
  methods: {
    init() {
      this.initViewer()
      if (this.items) this.loadTileSources()
    },
    initViewer() {
      if (this.viewer) this.viewer.destroy()
      this.$nextTick(() => {
        this.viewer = OpenSeadragon({
          id: 'osd',
          prefixUrl: 'https://openseadragon.github.io/openseadragon/images/',
        })
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
    items (items) { if (items) this.loadTileSources() },
    tileSources: {
      handler: function () {
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
