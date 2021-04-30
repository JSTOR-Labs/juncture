<template>
  <div class="osd" id="osd" :style="containerStyle"></div>
</template>

<script>

const prefixUrl = 'https://openseadragon.github.io/openseadragon/images/'

module.exports = {
  name: 've-osd',
  props: {
    items: { type: Array, default: () => ([]) },
    active: Boolean
  },
  data: () => ({
    viewerLabel: 'OpenSeadragon Viewer',
    viewerIcon: 'fas fa-dragon',
    dependencies: ['https://cdn.jsdelivr.net/npm/openseadragon@2.4/build/openseadragon/openseadragon.min.js'],
    osd: null
  }),
  computed: {
    containerStyle() { return { height: this.active ? '100%' : '0' } },
    tileSources() { return this.items
      .filter(item => item[this.$options.name])
      .map(item => { return { tileSource: { url: item.url, type: 'image', buildPyramid: true }} })
    }
  },
  mounted() { this.loadDependencies(this.dependencies, 0, this.init) },
  methods: {
    init() { this.osdInit() },
    osdInit() {
      if (this.active && !this.osd)
        this.osd = OpenSeadragon({
          id: 'osd', prefixUrl,
          homeFillsViewer: true,
          sequenceMode: true,
          showReferenceStrip: true
        })
      this.osd.open(this.tileSources)
    }
  },     
  watch: {
    tileSources() { if (this.osd) this.osd.open(this.tileSources) },
    active() { this.osdInit() }
  }
}

</script>

<style>
</style>
