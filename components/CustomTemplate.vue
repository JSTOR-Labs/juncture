<template>
  <div :style="containerStyle">
    Custom Component
  </div>
</template>

<script>

module.exports = {
  name: 've-custom',
  props: {
    items: { type: Array, default: () => ([]) },
    active: Boolean
  },
  data: () => ({
    viewerLabel: 'Custom Component',
    viewerIcon: 'fas fa-code',
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
