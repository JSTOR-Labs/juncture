<template>
  <div ref="player" class="text-xs-center">
    <!--
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
    
  <iframe
    v-if="playerWidth"
    :src="videoId"
    :width="playerWidth - 12">
  </iframe>
  -->
    <video
   id=”my-player”
   class=”video-js”
   controls
   preload=”auto”
   poster=”//vjs.zencdn.net/v/oceans.png”
   data-setup=’{}’>
   <source src=”https://www.youtube.com/watch?v=_VwKvS6QpsI" type=”video/mp4"></source>
   </video>
  </div>
</template>

<script>

const viewerLabel = 'Video Viewer'
const viewerIcon = 'fas fa-video'
const dependencies = ['https://cdnjs.cloudflare.com/ajax/libs/plyr/3.6.7/plyr.min.js',
  'https://vjs.zencdn.net/7.11.4/video.min.js',
  'https://vjs.zencdn.net/7.11.4/video-js.css',
  'https://cdnjs.cloudflare.com/ajax/libs/videojs-vimeo/2.0.2/video.js',
  'https://cdnjs.cloudflare.com/ajax/libs/videojs-youtube/2.0.4/Youtube.min.js']

module.exports = {
  name: 've-video',
  props: {
    items: { type: Array, default: () => ([]) }
  },
  data: () => ({
    viewerLabel,
    viewerIcon,
    dependencies,
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
    //player() { return this.$refs.youtube ? this.$refs.youtube.player : null }
  },
  mounted() {
    console.log('video component');
    console.log(`${this.$options.name}.mounted: height=${this.height} width=${this.width}`, this.mapDef)
    this.loadDependencies(dependencies, 0, this.init)
  },
  /*
  beforeDestroy() {
    this.isPlaying = false
    if (this.isPlaying) {
      this.player.stopVideo()
    }
  },
  */
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
