<template>
  <div id="footer-component">
    Footer <img v-if="logo" :src="logo">
  </div>
</template>

<script>

  module.exports = {  
    name: 'Footer',
    props: {
      siteConfig: { type: Object, default: function(){ return {}} },
      contentSource:  { type: Object, default: () => ({}) }
    },
    data: () => ({}),
    computed: {
      logo() { return this.siteConfig ? this.siteConfig.logo : null }
    },
    mounted() {},
    methods: {},
    watch: {}
  }

</script>

<style>
  
  [v-cloak] { display: none; }

  #footer-component {
    display: flex;
    align-items: center;
    height: 50px;
    background-color: #ffffff;
  } 
  #footer-component img {
    height: 30px;
    margin: 0 12px;
  }

</style>