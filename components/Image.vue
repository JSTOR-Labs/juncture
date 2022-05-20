<template>
  <div :style="containerStyle">

    <ve-image :user="user" :anno-base="path" height="100%" width="100%">
      <ul>
        <li v-for="(item, idx) in imageData" :key="idx">{{item}}</li>
      </ul>
    </ve-image>

  </div>  
</template>

<script>

module.exports = {
  name: 've2-image',
  props: {
    items: { type: Array, default: () => ([]) },
    contentSource:  { type: Object, default: () => ({}) },
    mdDir:  String,
    viewerIsActive: Boolean
  },
  data: () => ({
    viewerLabel: 'Image Viewer',
    viewerIcon: 'far fa-file-image',
    dependencies: []
  }),
  computed: {
    containerStyle() { return { height: this.viewerIsActive ? '100%' : '0' } },
    viewerItems() { return this.items.filter(item => item.viewer === 've-image') },
    imageData() { return this.viewerItems.map(item => {
      let entry = item.manifest || item.src ? item.manifest || item.src : `/${item.url}`
      if (item.fit) entry += ` ${item.fit}`
      if (item.region) entry += ` ${item.region}`
      return entry
    }) 
    },
    user() { return this.contentSource.acct },
    basePath() { return this.contentSource.basePath.split('/').filter(elem => elem).slice(this.contentSource.isGhpSite ? 1 : 0).join('/') },
    path() { return `${this.basePath}${this.mdDir}` }
  },
  mounted() { this.loadDependencies(this.dependencies, 0, this.init) }
}

</script>

<style>
</style>
