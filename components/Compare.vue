<template>
  <div :style="containerStyle">

    <ve-image :compare="mode">
      <ul>
        <li v-for="(image, idx) in images" :key="idx">{{image.manifest || image.src}}{{image.region ? ' '+image.region : ''}}</li>
      </ul>
    </ve-image>

  </div>  
</template>

<script>

module.exports = {
  name: 've2-image',
  props: {
    items: { type: Array, default: () => ([]) },
    viewerIsActive: Boolean
  },
  data: () => ({
    viewerLabel: 'Image Compare',
    viewerIcon: 'fas fa-images',
    dependencies: []
  }),
  computed: {
    containerStyle() { return { height: this.viewerIsActive ? '100%' : '0' } },
    images() { return this.items.filter(item => item.viewer === 've-compare') },
    mode() { let firstItemWithMode = this.images.find(item => item.compare)
             return firstItemWithMode ? firstItemWithMode.compare : 'curtain'
    }
  },
  mounted() { this.loadDependencies(this.dependencies, 0, this.init) }
}

</script>

<style>
</style>
