<template>
  <div id = "wrapper">
    <p>
      <a href = '#A'>a</a> |
      <a href = '#B'>b</a> |
      <a href = '#C'>c</a> |
      <a href = '#D'>d</a> |
      <a href = '#E'>e</a> |
      <a href = '#F'>f</a> |
      <a href = '#G'>g</a> |
      <a href = '#H'>h</a> |
      <a href = '#I'>i</a> |
      <a href = '#J'>j</a> |
      <a href = '#K'>k</a> |
      <a href = '#L'>l</a> |  
      <a href = '#M'>m</a> |
      <a href = '#N'>n</a> |
      <a href = '#O'>o</a> |
      <a href = '#P'>p</a> |
      <a href = '#Q'>q</a> |
      <a href = '#R'>r</a> |  
      <a href = '#S'>s</a> |
      <a href = '#T'>t</a> |
      <a href = '#U'>u</a> |
      <a href = '#V'>v</a> |
      <a href = '#W'>w</a> |
      <a href = '#X'>x</a> |  
      <a href = '#Y'>y</a> |
      <a href = '#Z'>z</a>
    </p>
    <div class="reviews" id = "reviews_container" @onload="sortCards()">
      <div v-for="(review, cidx) in locations" :key="`review-${cidx}`">
        <h2 v-if="review.heading" v-html="review.heading"></h2>
        <div v-if="review.content.length > 0" class="review-text">
          <div>
            <p v-for="(contentItem, ccidx) in review.content" :key="`${cidx}-${ccidx}`" :id="contentItem.id" 
              :class="contentItem.classes.join(' ')"
              v-html="contentItem.html"
            ></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<!--
<template>
  <div class = "reviews clamp-10" id = "reviews_container">
    <div v-for="(review, aidx) in reviews"
        :key="`review-${aidx}`" :id="review.heading.charAt(0)" :class="review.classes.join(' ')"
      >
      <h2 v-if="review.heading" v-html="review.heading">
      <div class = "clamp-wrapper">
        <p v-if="review.text" v-html="review.text"></p>
      </div>
    </div>
  </div>
</template>
-->
<script>
module.exports = {
  name: 'Reviews',
  props: {
    locations: {type: Array, default: () => ([])},
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
  methods: {},
  watch: {}
}
</script>

<style>
#header {
  display: unset;
}
#reviews_container {
  padding: 58px 3% 0 3%;
  font-family: Roboto, 'sans-serif';
}
#reviews_container > h2 {
  font-size: 30px;
  font-weight: normal;
}
#reviews_container > #para {
  padding: 0 0 2vh 0;
}
</style>
