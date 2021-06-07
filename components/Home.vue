<template>
  <div id="home" :class="{'fixed-header': fixedHeader}">

    <!-- Pure CSS hamburger menu - https://codepen.io/mutedblues/pen/MmPNPG -->
    <header>
      <a href="" class="logo">Juncture</a>
      <input class="menu-btn" type="checkbox" id="menu-btn" />
      <label class="menu-icon" for="menu-btn"><span class="navicon"></span></label>
      <ul class="menu">
        <li @click="doMenuAction('loadEssay', '/about')"><i :class="`fas fa-info`"></i>About</li>
        <li @click="doMenuAction('toggleContactForm')"><i :class="`fas fa-envelope`"></i>Contact us</li>
      </ul>
    </header>

    <main>
      <section v-for="(section, sidx) in content" :key="sidx">
        <h1 v-if="section.heading" v-html="section.heading"></h1>
        <div class="home-cards">
          <div v-for="(card, cidx) in section.cards" :key="`${sidx}-${cidx}`" 
              :class="`${section.cards.length === 1 ? 'card-1' : 'card-n'}`">
            <img v-if="card.image" :src="card.image">
            <h2 v-if="card.heading" v-html="card.heading"></h2>
            <div class="card-text">
              <p v-for="(para, pidx) in card.text" :key="`${sidx}-${cidx}-${pidx}`" v-html="para"></p>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer>
      Footer
    </footer>

    <div id="home-contact-form" class="modal-form" style="display: none;">
      <form v-on:submit.prevent>
        <h1>Contact us</h1>
        <input v-model="contactName" name="name" placeholder="Name" class="form-name" type="text" required>
        <input v-model="contactEmail" placeholder="Email" class="form-email" type="email" required>
        <textarea v-model="contactMessage" placeholder="Your message here" class="form-message" type="text" required></textarea>
        <div v-html="doActionResponse.message"></div>
        <div class="form-controls">
          <button v-if="!doActionResponse.status" class="form-cancel" formnovalidate @click="hideForm">Cancel</button>
          <button v-if="!doActionResponse.status" class="form-submit" @click="submitContactForm">Send</button>
          <button v-if="doActionResponse.status === 'done'" class="form-submit" @click="hideForm">Close</button>
        </div>
      </form>
    </div>

  </div>
</template>

<script>

const dependencies = []

module.exports = {  
  name: 'juncture-home',
  props: {
    html: { type: String, default: '' },
  },
  data: () => ({
    fixedHeader: true,
    content: {},
    doActionResponse: {},
    contactName: '',
    contactEmail: '',
    contactMessage: ''
  }),
  computed: {},
  mounted() {
    let app = document.getElementById('app')
    Array.from(app.classList).forEach(cls => app.classList.remove(cls))
    this.loadDependencies(dependencies, 0, this.init)
  },
  methods: {
    init() {},
    loadPage() {
      console.log('loadPage')
      this.$emit('do-action', 'loadEssay', '/examples')
    },
    
    // Creates content object from input HTML
    parseHtml(html) {
      let root = new DOMParser().parseFromString(html, 'text/html').children[0].children[1]
      return Array.from(root.querySelectorAll(':scope > section')).map(section => {
        return {
          id: section.id,
          heading: section.querySelector('h1, h2, h3, h4, h5, h6').innerHTML,
          cards: Array.from(section.querySelectorAll(':scope > section')).map(el => {
            let card = {}
            Object.entries({
              image: 'p img',
              heading: 'h1, h2, h3, h4, h5, h6'
            }).forEach(entry => {
              let [fld, selector] = entry
              let found = el.querySelector(selector)
              if (found) card[fld] = found.tagName === 'IMG' ? found.src : found.innerHTML
            })
            card.text = Array.from(el.querySelectorAll('p')).filter(p => p.textContent).map(p => p.innerHTML)
            return card
          })
        }
      })
    },

    doMenuAction(action, options) {
      console.log(`doMenuAction=${action}`, options)
      if (action === 'toggleContactForm') {
        this.toggleContactForm()
      } else {
        // this.$emit('do-action', action, options)
      }
    },

    toggleContactForm() {
      let formId = 'home-contact-form'
      if (document.getElementById(formId).style.display === 'none') this.showForm(formId)
      else this.hideForm()
    },

    showForm(formId) {
      document.getElementById('home').classList.add('dimmed')
      let form = document.getElementById(formId)
      form.style.display = 'unset'
      form.classList.add('visible-form')
    },

    hideForm() {
      document.getElementById('home').classList.remove('dimmed')
      let form = document.querySelector('.visible-form')
      form.style.display = 'none'
      form.classList.remove('visible-form')
      this.doActionResponse = {}
    },

    submitContactForm() {
      console.log('submitContactForm')
    }
  
  },
  watch: {
    html: {
      handler: function (html) {
        if (html) this.content = this.parseHtml(html)
      },
      immediate: true
    }
  }
}

</script>

<style>

  #home {
    display: flex;
    flex-direction: column;
    height: 100vh;
    position: relative;
  }

  #home section {
    border: 1px solid red;
    padding: 12px;
    background-color: white;
  }

  #home section:nth-child(even) {
    background-color: #ddd;
  }

  #home section h1 {
    text-align: center;
  }

  .home-cards {
    display: grid;
    grid-auto-flow: row;
    gap: 1em;
  }

  .card-n {
    display: flex;
    flex-direction: column;
  }

  .card-1 {
    display: grid;
    grid-template-rows: auto auto;
    grid-template-columns: 50% 50%;
    align-items: flex-start;
    grid-template-areas: 
      "card-heading card-image"
      "card-text    card-image"
      ;
  }

  .card-1 img {
    grid-area: card-image;
    align-self: center;
  }

  .card-1 h2 {
    grid-area: card-heading;
  }

  .card-text {
    grid-area: card-text;
  }

  img {
    width: 100%;
    border-radius: 12px;
  }

  @media (min-width: 55em) {
    .home-cards {
      grid-auto-flow: column !important;
    }
  }

body {
  margin: 0;
  font-family: Helvetica, sans-serif;
  background-color: #f4f4f4;
}

a {
  color: #000;
}

#home.fixed-header main {
  padding-top: 58px;
}

footer {
  color: white;
  background-color: #999;
  padding: 12px 24px;
}

/* Pure CSS hamburger menu */
/* https://codepen.io/mutedblues/pen/MmPNPG */

/* header */

header {
  background-color: #fff;
  box-shadow: 1px 1px 4px 0 rgba(0,0,0,.1);
  width: 100%;
  z-index: 3;
}

#home.fixed-header header {
  position: fixed;
}

header ul {
  margin: 0;
  padding: 0;
  list-style: none;
  overflow: hidden;
  background-color: #eee;
}

header li {
  display: block;
  padding: 10px 20px;
  border-right: 1px solid #f4f4f4;
  color: #0164b9;
  text-decoration: none;
}

header li svg {
  margin-right: 6px;
  min-width: 20px;
}

header li:hover,
header .menu-btn:hover {
  background-color: #f4f4f4;
}
header li:hover {
  cursor: pointer;
}

header .logo {
  display: block;
  float: left;
  font-size: 2em;
  padding: 10px 20px;
  text-decoration: none;
}

/* menu */

header .menu {
  clear: both;
  max-height: 0;
  transition: max-height .2s ease-out;
}

/* menu icon */

header .menu-icon {
  cursor: pointer;
  display: inline-block;
  float: right;
  padding: 28px 20px;
  position: relative;
  user-select: none;
}

header .menu-icon .navicon {
  background: #333;
  display: block;
  height: 2px;
  position: relative;
  transition: background .2s ease-out;
  width: 18px;
}

header .menu-icon .navicon:before,
header .menu-icon .navicon:after {
  background: #333;
  content: '';
  display: block;
  height: 100%;
  position: absolute;
  transition: all .2s ease-out;
  width: 100%;
}

header .menu-icon .navicon:before {
  top: 5px;
}

header .menu-icon .navicon:after {
  top: -5px;
}

/* menu btn */

header .menu-btn {
  display: none;
}

header .menu-btn:checked ~ .menu {
  max-height: 240px;
}

header .menu-btn:checked ~ .menu-icon .navicon {
  background: transparent;
}

header .menu-btn:checked ~ .menu-icon .navicon:before {
  transform: rotate(-45deg);
}

header .menu-btn:checked ~ .menu-icon .navicon:after {
  transform: rotate(45deg);
}

header .menu-btn:checked ~ .menu-icon:not(.steps) .navicon:before,
header .menu-btn:checked ~ .menu-icon:not(.steps) .navicon:after {
  top: 0;
}

/* 48em = 768px */

@media (min-width: 48em) {
  header li {
    float: left;
  }
  header ul {
    background-color: #fff;
  }
  header li {
    padding: 20px 10px;
  }
  header .menu {
    clear: none;
    float: right;
    max-height: none;
  }
  header .menu-icon {
    display: none;
  }
}

</style>