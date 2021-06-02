<template>
  <div ref="main" v-html="html"></div>
</template>

<script>

module.exports = {  
  name: 'custom-main',
  props: {
    html: { type: String, default: '' }
  },
  data: () => ({}),
  computed: {},
  mounted() {},
  methods: {},
  watch: {}
}

</script>

<style>
</style>