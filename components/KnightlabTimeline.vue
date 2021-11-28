<template>
  <div :style="containerStyle">
    <iframe 
      :src="`https://cdn.knightlab.com/libs/timeline3/latest/embed/index.html?source=${item.source}&font=Default&lang=en&timenav_position=${item['timenav-position'] || 
            'bottom'}&hash_bookmark=${item['hash_bookmark'] || 
            'false'}&initial_zoom=${item['initial-zoom'] || '2'}&height=${item.height || '650'}`"
      width="100%" 
      height="100%" 
      webkitallowfullscreen mozallowfullscreen allowfullscreen 
      frameborder="0">
    </iframe>
  </div>  
</template>
<script>

module.exports = {
  name: 'TimelineViewer',
  props: { 
    items: { type: Array, default: () => ([]) },
    viewerIsActive: Boolean
  },
  data: () => ({
    viewerLabel: 'Knightlab Timeline',
    viewerIcon: 'fas fa-history',
    dependencies: [],
    height: 750,
  }),
  computed: {
    containerStyle() { return { 
      position: 'relative',
      height: this.viewerIsActive ? '100%' : '0', 
      overflowY: 'auto !important' 
    }},
    filteredItems() { return this.items.filter(item => item[this.componentName]) },
    item() { return this.filteredItems[0] }
  },
  mounted() { this.loadDependencies(this.dependencies, 0, this.init) },
  methods: {
    init() {
      // console.log(`${this.componentName}: height=${this.height} width=${this.width}`)
    }
  }
}
</script>

<style>
</style>