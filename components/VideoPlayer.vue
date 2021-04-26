<template>
  <div ref="player" class="text-xs-center">
    <youtube
      v-if="playerWidth"
      ref="youtube"
      :fit-parent="true"
      :resize="true"
      :video-id="videoId"
      :width="playerWidth - 12"
      :player-vars="playerVars"
      @ready="ready"
      @playing="playing"
      @paused="paused"
      class="youtube-iframe"
    />
  </div>
</template>

<script>

const dependencies = []

module.exports = {
  name: 'VideoPlayer',
  props: {
    items: { type: Array, default: () => ([]) }
  },
  data: () => ({
    playerVars: {
      ytppauseoverlay: 0,
      modestbranding: 1,
      rel: 0,
      showinfo: 0,
      autohide: 1,
      playsinline: 1
    },
    isPlaying: false,
    playerWidth: 564
  }),
  computed: {
    videoId() { return this.items[0].vid || this.items[0].id },
    player() { return this.$refs.youtube ? this.$refs.youtube.player : null }
  },
  mounted() {
    console.log(`${this.$options.name}.mounted: height=${this.height} width=${this.width}`, this.mapDef)
    this.loadDependencies(dependencies, 0, this.init)
  },
  beforeDestroy() {
    this.isPlaying = false
    if (this.isPlaying) {
      this.player.stopVideo()
    }
  },
  methods: {
    init() {

    },
    playVideo() {
      this.player.playVideo()
    },
    playing() {
      this.isPlaying = true
    },
    paused() {
      this.isPlaying = false
    },
    ready() {
      // console.log('Video player ready')
    }
  }
}
</script>

<style>
  .youtube-iframe {
    position: absolute;
    margin-top: 64px;
  }
</style>
