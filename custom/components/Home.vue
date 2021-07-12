<template>

  <main class="dofe-home">

    <template v-for="(section, idx) in content">
      <section id = "intro-section" v-if="!section.cards" :key="`section-${idx}`">
        <h1 v-if="section.heading" v-html="section.heading"></h1>
        <div v-if="section.html" v-html="section.html"></div>
      </section>
    </template>

    <section>
      <ul class="navbar">
        <li :class="{'active': tab === 'map'}" @click="tab = 'map'"><i class="fas fa-map"></i> Map</li>
        <li :class="{'active': tab === 'cards'}" @click="tab = 'cards'"><i class="fas fa-th-large"></i> Cards</li>
      </ul>
    </section>

    <section>
      <ve-map v-if="tab === 'map'" :locations="locations" @do-action="doAction"></ve-map>
      <ve-cards v-if="tab === 'cards'" :locations="locations" @do-action="doAction"></ve-cards>
    </section>

  </main>

</template>

<script>

module.exports = {
  name: 'Home',
  props: {
    html: {type: String, default: ''}
  },
  data: () => ({
    content: [],
    tab: 'cards'
  }),
  computed: {
    locations() { 
      let resp = this.content.filter(item => item.cards !== undefined).map(item => item.cards.content)
      return resp.length > 0 ? resp[0] : []
    }
  },
  mounted() { 
    document.getElementById('app').classList.add('visual-essay')
  },
  methods: {

    doAction(options) {
      if (options.action === 'load-page') this.$emit('do-action', 'load-page', options.path)
    },

    // Creates content object from input HTML
    parseHtml(html) {
      let root = new DOMParser().parseFromString(html, 'text/html').children[0].children[1]
      return Array.from(root.querySelectorAll(':scope > section')).map(section => {
        
        let classes = new Set(section.className.split(' ').filter(cls => cls !== ''))
        let backgroundImage = section.querySelector('p.background-image > img')
        let html = segments = Array.from(section.querySelectorAll(':scope > .segment'))
          .filter(el => !el.querySelector('.background-image'))
          .map(el => el.innerHTML).join(' ')
        let cards, subsections
        
        let cardsSection = section.querySelector(':scope > section.cards')
        if (cardsSection) {
          // cardsSection.className.split(' ').filter(cls => cls !== '').forEach(cls => classes.add(cls))
          let cardClasses = new Set(cardsSection.className.split(' ').filter(cls => cls !== ''))
          if (cardClasses.has('carousel')) cardClasses.delete('cards')
          cards = {
            classes: cardClasses,
            content: Array.from(cardsSection.querySelectorAll('section'))
              .map(el => {
                let card = {}
                if (el.id) card.id = el.id
                if (el.className) card.classes = new Set(el.className.split(' ').filter(cls => cls !== ''))
                Object.entries({
                  media: 'video, p img',
                  heading: 'h1, h2, h3, h4, h5, h6',
                  metadata: 'pre'
                }).forEach(entry => {
                  let [fld, selector] = entry
                  let found = el.querySelector(selector)
                  if (found) {
                    if (fld === 'metadata') {
                      // Create metadata object from key-value pairs in code block
                      card[fld] = Object.fromEntries(
                        found.textContent.split('\n')
                        .filter(rec => rec.trim() !== '')
                        .map(rec => rec.split(':').map(elem => elem.trim())))
                    } else {
                      card[fld] = fld === 'media' ? found.outerHTML : found.innerHTML
                    }
                  }
                })
                card.content = Array.from(el.querySelectorAll('p, ul, ol'))
                  .filter(cc => cc.textContent)
                  .map(cc => {
                    return {
                      html: cc.tagName === 'P' ? cc.innerHTML : cc.outerHTML, 
                      id: cc.id, 
                      classes: new Set(cc.className.split(' ').filter(cls => cls !== ''))
                    }
                  })
                if (card.heading) card.slug = slugify(card.heading)
                return card
              })
          }
        }
                
        if (!cards) {
          subsections = Array.from(section.querySelectorAll(':scope > section'))
            .map(el => { return { html: el.innerHTML, classes: new Set() } })
        }

        let result = {
          heading: section.querySelector('h1, h2, h3, h4, h5, h6').innerHTML,
          classes, 
          html
        }
        if (section.heading) section.slug = slugify(section.heading)
        if (section.id) result.id = section.id
        if (backgroundImage) result.backgroundImage = backgroundImage.src
        if (cards) result.cards = cards
        if (subsections) result.subsections = subsections

        return result
      })
    }

  },
  watch: {
    html: {
      handler: function (html) {
        if (html) {
          this.content = this.parseHtml(html)
          this.$nextTick(() => this.convertLinks(document.getElementById('essay')))
        }
      },
      immediate: true
    }
  }
}

</script>

<style>

.visual-essay #essay {
  padding: 58px 0 0 0;
}

.dofe-home {
  display: grid;
  grid-template-rows: auto auto 1fr;
  height: 100%;
}

/* Style the navigation bar */
ul.navbar {
  width: 100%;
  height: 46px;
  background-color: #555;
  overflow: auto;
  list-style: none;
  padding: 0;
  margin: 0;
}

/* Navbar links */
.navbar li {
  float: left;
  text-align: center;
  padding: 12px 24px;
  color: white;
  text-decoration: none;
  font-size: 17px;
  cursor: pointer;
}

/* Navbar links on mouse-over */
.navbar li:hover {
  background-color: #000;
}

/* Current/active navbar link */
.active {
  background-color: #04AA6D;
}

#intro-section {
  padding-left: 2%;
  padding-right: 2%;
}

.card {
  top: 25px !important;
}

.media img { 
  min-width: 100%;
  max-width: 100%;
  min-height: 4vh;
  max-height: 4vh;

}

/* Add responsiveness - will automatically display the navbar vertically instead of horizontally on screens less than 500 pixels */
/*
@media screen and (max-width: 500px) {
  .navbar li {
    float: none;
    display: block;
  }
}
*/

</style>