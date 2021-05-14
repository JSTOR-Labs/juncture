<template>
  <div v-html="viewerLabel" :style="containerStyle">
  </div>
</template>

<script>

module.exports = {
  name: 've-plant-specimen',
  props: {
    items: { type: Array, default: () => ([]) },
    active: Boolean
  },
  data: () => ({
    viewerLabel: 'Plant Specimen',
    viewerIcon: 'fas fa-seedling',
    dependencies: []
  }),
  computed: {
    containerStyle() { return { height: this.active ? '100%' : '0' } }
  },
  mounted() { this.loadDependencies(this.dependencies, 0, this.init) },
  methods: {
    init() {
      console.log(`${this.$options.name}.mounted`)
    }
  }
}

</script>

<style>
</style>
