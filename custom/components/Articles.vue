<template>
  <div id = "articles">
      <p>{{ articles_text }}</p>
  </div>
</template>

<script>

module.exports = {
  name: 'Articles',
  props: {
    locations: {type: Array, default: () => ([])}
  },
  data: () => ({
    map: null,
    articles_text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
  }),
  computed: {},
  mounted() {
    let root = document.getElementById('essay')
    this.convertLinks(root)
    const ps = document.querySelectorAll('.clamp-wrapper')
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        entry.target.classList[entry.target.scrollHeight > entry.contentRect.height ? 'add' : 'remove']('truncated')
      }
    })
    ps.forEach(p => observer.observe(p))
  },
  methods: {
      init() {
          this.articles_text = "Hello world."
      }
  },
  watch: {}
}

</script>

<style>

#header {
  display: unset;
}
#about {
  padding: 58px 3% 0 3%;
}

#about > #para {
  padding: 0 0 2vh 0;
}

</style>