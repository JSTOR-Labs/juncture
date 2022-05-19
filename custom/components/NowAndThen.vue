<template>
  <div id="now-and-then">
    <div id="para" v-html="html"></div>
    <h3>Mode</h3>
    <button type="button" :class="{'active': this.mode === 'curtain'}" class="toggle-mode" id="curtain-mode" @click="mode = 'curtain'">Curtain</button>
    <button type="button" :class="{'active': this.mode === 'sync'}" class="toggle-mode" id="sync-mode" @click="mode = 'sync'">Sync</button>
    <p class = "mode-description">{{ mode_description }}</p>
    
    <ve-image :compare="mode" height="100%">
      <ul>
        <li v-for="(image, idx) in images" :key="idx">{{image.manifest || image.src}}{{image.region ? ' '+image.region : ''}}</li>
      </ul>
    </ve-image>

  </div>
</template>

<script>

module.exports = {
  name: 'NowAndThen',
  props: {
    html: {type: String, default: ''},
    params: {type: Array, default: () => ([])}
  },
  data: () => ({
    viewer: null,
    mode: 'curtain',
    mode_description: 'Pinch in to zoom. Move your cursor from left to right to view now VS then.'
  }),
  computed: {
    containerStyle() { return { height: this.viewerIsActive ? '100%' : '0' } },
    images() { return this.params.filter(item => item.viewer === 've-compare') },
  },
  mounted() {},
  methods: {},
  watch: {}
}
</script>

<style>

#header {
  display: unset;
}

#now-and-then {
  padding: 58px 3% 0 3%;
  height: 100%;
}

#now-and-then > #para {
  padding: 0 0 2vh 0;
}

.toggle-mode {
  font-size: 1.2em;
  padding: 0.6%;
  border-radius: 10px;
  color: white;
  background-color: #555;
  border: 2px solid #555;

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

.mode-description {
  font-style: italic;
}

</style>
