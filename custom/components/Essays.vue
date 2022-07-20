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
    <div class="cards clamp-10" id = "cards_container" @onload="sortCards()">
      <div v-for="(card, cidx) in locations" 
        :key="`card-${cidx}`" :id="card.heading.charAt(0)" :class="card.classes.join(' ')"
      >
        <div v-if="card.media" class="media" v-html="card.media"></div>
        <h2 v-if="card.heading" v-html="card.heading" @click="cardSelected(card.slug)"></h2>
        <div v-if="card.content.length > 0" class="card-text">
          <input type="checkbox" :id="`exp-${cidx}`">
          <div class="clamp-wrapper">
            <p v-for="(contentItem, ccidx) in card.content" :key="`${cidx}-${ccidx}`" :id="contentItem.id" 
              :class="contentItem.classes.join(' ')"
              v-html="contentItem.html"
            ></p>
          </div>
          <label :for="`exp-${cidx}`" role="button">more</label>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

module.exports = {
  name: 'Cards',
  props: {
    locations: {type: Array, default: () => ([])}
  },
  data: () => ({
    map: null
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

    // Sort cards alphabetically
    var cards_container = document.getElementById('cards_container')
    var cards = cards_container.getElementsByClassName('card');

    [].slice.call(cards).sort(function(a, b) {
      var a_heading = a.getElementsByTagName('h2')[0].innerHTML
      var b_heading = b.getElementsByTagName('h2')[0].innerHTML
      return a_heading.localeCompare(b_heading)
    }).forEach(function(val, index1) {
      cards_container.appendChild(val)
    })

  },
  methods: {
    cardSelected(slug) {
      console.log(`cardSelected: slug=${slug}`)
      this.$emit('do-action', {action: 'load-page', path: `/essays/${slug}`})
    },
  },
  watch: {}
}

</script>

<style>

#wrapper > p {
  margin-left: 3%;
  margin-right: 3%
}

/************ Cards ***********/

.cards {
  padding: 1em;
  height: 100%;
  display: grid;
  grid-template-columns: 100%;
  grid-column-gap: 0;
  grid-row-gap: 20px;
}


.card {
  padding: 12px;
}

@media only screen and (min-width: 640px) {
  .cards {
    grid-template-columns: 47.5% 47.5%;
    grid-column-gap: 5%;
    grid-row-gap: 40px;
  }
}

@media only screen and (min-width: 981px) {
  .cards {
    grid-template-columns: 30% 30% 30%;
    grid-row-gap: 50px;
  }
}

.card:hover {
  cursor: pointer;
  border: 1px solid #ddd;
}

.card h2 {
  /* margin-top: 40px; */
  margin-bottom: 0;
  font-weight: 400;
}

.card .media {
  text-align: center;
}

.media img { 
  width: 100%;
  height: 250px;
  object-fit: cover;
}

.card .media video {
  border-radius: 8px;
}

.card p {
  font-size: 18px;
  font-weight: 300;
  line-height: 1.4;
  margin: 0;
}

.card p:first-of-type {
  padding-top: 20px;
}

.horizontal .card {
  display: grid;
  grid-template-rows: auto auto;
  grid-template-columns: 50% 50%;
  grid-column: 1/span3;
  align-items: flex-start;
  grid-template-areas:
    "card-heading card-media"
    "card-text    card-media";
}
.horizontal .card h2 {
  margin-top: 0;
  grid-area: card-heading;
  font-family: Georgia, 'serif';
  font-size: 30px;
  font-weight: normal;
}
.horizontal .card .card-text {
  grid-area: card-text;
}.horizontal .card .media {
  grid-area: card-media;
}

.card input, .card label {
  display: none;
}
/************ End Cards ***********/

/************ Card text clamping ***********/
.clamp input, .clamp-5 input, .clamp-10 input, .clamp-15 input, .clamp-20 input,
.clamp label, .clamp-5 label, .clamp-10 label, .clamp-15 label, .clamp-20 label {
  display: unset;
}

.clamp input, .clamp-5 input, .clamp-10 input, .clamp-15 input, .clamp-20 input {
  display: none;
  opacity: 0;
  position: absolute;
  pointer-events: none;
}
.clamp .clamp-wrapper,
.clamp-5 .clamp-wrapper,
.clamp-10 .clamp-wrapper,
.clamp-15 .clamp-wrapper,
.clamp-20 .clamp-wrapper {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 6px;
}
.clamp-5 .clamp-wrapper { -webkit-line-clamp: 5; }
.clamp-10 .clamp-wrapper { -webkit-line-clamp: 10; }
.clamp-15 .clamp-wrapper { -webkit-line-clamp: 15; }
.clamp-20 .clamp-wrapper { -webkit-line-clamp: 20; }

.clamp-wrapper p {
  margin-block-start: 0;
}

.clamp input:focus ~ label,
.clamp-5 input:focus ~ label,
.clamp-10 input:focus ~ label,
.clamp-15 input:focus ~ label,
.clamp-20 input:focus ~ label {
	outline: -webkit-focus-ring-color auto 5px;
}
.clamp input:checked + div,
.clamp-5 input:checked + div,
.clamp-10 input:checked + div,
.clamp-15 input:checked + div,
.clamp-20 input:checked + div {
	-webkit-line-clamp: unset;
}
.clamp input:checked ~ label,
.clamp-5 input:checked ~ label, 
.clamp-10 input:checked ~ label, 
.clamp-15 input:checked ~ label, 
.clamp-20 input:checked ~ label, 
.clamp-wrapper:not(.truncated) ~ label {
  display: none;
}
.clamp label,
.clamp-5 label,
.clamp-10 label,
.clamp-15 label,
.clamp-20 label {
  border-radius: 4px;
  padding: 0.2em 0.6em 0.3em 0.6em;
  border: 1px solid #605C2A;
  background-color: #605C2A;
  color: #fff;
  font-size: 0.8em;
  cursor: pointer;
}
/************ End Card text clamping ***********/

</style>
