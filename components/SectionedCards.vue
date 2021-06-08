<template>
  <div id="home" :class="{'fixed-header': fixedHeader}">

    <!-- Pure CSS hamburger menu - https://codepen.io/mutedblues/pen/MmPNPG -->
    <header v-if="fixedHeader">
      <img class="logo" @click="doMenuAction('loadEssay', '/')" :src="logo">
      <input class="menu-btn" type="checkbox" id="menu-btn"/>
      <label class="menu-icon" for="menu-btn"><span class="navicon"></span></label>
      <ul class="menu">
        <li v-for="navItem in nav" :key="navItem.path" @click="doMenuAction('loadEssay', navItem.path)">
          <i v-if="navItem.icon" :class="navItem.icon"></i>{{ navItem.label }}
        </li>
      </ul>
    </header>

    <main>

      <section v-for="(section, sidx) in content" :key="sidx" :class="section.classes.join(' ')">

        <template v-if="section.classes.has('heading')">
          <header v-if="!fixedHeader">
            <img class="logo" @click="doMenuAction('loadEssay', '/')" :src="logo">
            <input class="menu-btn" type="checkbox" id="menu-btn"/>
            <label class="menu-icon" for="menu-btn"><span class="navicon"></span></label>
            <ul class="menu">
              <li v-for="navItem in nav" :key="navItem.path" @click="doMenuAction('loadEssay', navItem.path)">
                <i v-if="navItem.icon" :class="navItem.icon"></i>{{ navItem.label }}
              </li>
            </ul>
          </header>
          <div class="card-text" :style="`backgroundImage: url(${section.backgroundImage})`">
            <p v-for="(para, pidx) in section.cards[0].content" :key="pidx" :class="para.classes.join(' ')"
               v-html="para.text"></p>
          </div>
        </template>

        <template v-else>
          <h1 v-if="section.heading" v-html="section.heading"></h1>
          <div class="home-cards">
            <div v-for="(card, cidx) in section.cards" :key="`${sidx}-${cidx}`"
                 :class="`${section.cards.length === 1 ? 'card-1' : 'card-n'}`">
              <img v-if="card.image" :src="card.image">
              <h2 v-if="card.heading" v-html="card.heading"></h2>
              <div class="card-text">
                <p v-for="(para, pidx) in card.content" :key="`${sidx}-${cidx}-${pidx}`" :class="para.classes.join(' ')"
                   v-html="para.text"></p>
              </div>
            </div>
          </div>
        </template>
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
        <textarea v-model="contactMessage" placeholder="Your message here" class="form-message" type="text"
                  required></textarea>
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
  name: 'SectionedCards',
  props: {
    html: {type: String, default: ''},
    params: {type: Array, default: () => ([])}
  },
  data: () => ({
    content: {},
    doActionResponse: {},
    contactName: '',
    contactEmail: '',
    contactMessage: ''
  }),
  computed: {
    nav() {
      return this.params.filter(param => param.nav)
    },
    config() {
      return this.params.find(param => param['ve-config']) || {}
    },
    fixedHeader() {
      return this.config['fixed-header'] === true
    },
    logo() {
      return this.config.logo
    }
  },
  mounted() {
    let app = document.getElementById('app')
    Array.from(app.classList).forEach(cls => app.classList.remove(cls))
    this.loadDependencies(dependencies, 0, this.init)
  },
  methods: {
    init() {
    },
    loadPage() {
      console.log('loadPage')
      this.$emit('do-action', 'loadEssay', '/examples')
    },

    // Creates content object from input HTML
    parseHtml(html) {
      let root = new DOMParser().parseFromString(html, 'text/html').children[0].children[1]
      return Array.from(root.querySelectorAll(':scope > section')).map(section => {
        console.log(section)
        let backgroundImage = section.querySelector('p.background-image > img')
        return {
          id: section.id,
          heading: section.querySelector('h1, h2, h3, h4, h5, h6').innerHTML,
          backgroundImage: backgroundImage ? backgroundImage.src : '',
          classes: new Set(section.classList),
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
            card.content = Array.from(el.querySelectorAll('p'))
                .filter(p => p.textContent)
                .map(p => {
                  return {text: p.innerHTML, id: p.id, classes: Array.from(p.classList)}
                })
            return card
          })
        }
      })
    },

    doMenuAction(action, options) {
      console.log(`doMenuAction=${action}`, options)
      if (action === 'loadEssay') {
        if (options === '/contact-us') {
          this.toggleContactForm()
        } else {
          this.$emit('do-action', action, options)
        }
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
    color: black;
  }

  #home section {
    padding: 72px 24px;
    background-color: white;
  }

  #home section:nth-child(odd) {
    background-color: #F5F5F5;
  }

  #home section h1 {
    text-align: center;
    font-family: Georgia, 'serif';
    font-size: 30px;
    margin-bottom: 40px;
  }

  #home section.heading {
    display: grid;
    grid-template-rows: 58px 1fr;
    padding: 0;
    min-height: 400px;
  }

  #home section.heading header {
    grid-area: 1 / 1 / 2 / 2;
  }

  #home section.heading div {
    grid-area: 1 / 1 / 3 / 2;
    /* padding-top: 58px; */
    align-self: center;
    justify-self: stretch;
    height: 100%;
    background-repeat: no-repeat;
    background-position: center center;
    background-size: cover;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: center;
    color: white;
  }

  #home section.heading p {
    font-size: 2.5em;
    font-family: Georgia, 'serif';
    font-weight: normal;
    line-height: 1.2;
    padding: 0;
    margin-left: 20%;
    margin-right: 20%;
    margin-top: 40px;
    margin-bottom: 0;
    text-align: center;
    color: white;
  }

  .heading header, .heading header ul, .heading header li {
    background-color: transparent;
    color: white;
    border-right: none;
  }

  .heading header li:hover {
    background-color: transparent;
    text-decoration: underline;
  }

  #home section p {
    font-size: 18px;
  }

  p.button {
    margin-top: 20px;
    text-align: center;
  }

  .button a {
    color: #000 !important;
    background-color: #FFE55A;
    border-radius: 50px;
    text-decoration: none;
    font-size: 30px;
    font-family: Roboto, 'sans-serif';
    padding: 16px 72px;
  }

  .home-cards {
    display: grid;
    grid-auto-flow: row;
    gap: 1.8em;
  }

  .card-n {
    display: flex;
    flex-direction: column;
    margin-bottom: 8px;
  }

  .card-n h2 {
    margin-top: 40px;
    margin-bottom: 0;
    font-weight: 400;
  }

  .card-1 {
    display: grid;
    grid-template-rows: auto auto;
    grid-template-columns: 50% 50%;
    align-items: flex-start;
    grid-template-areas:
        "card-heading card-image"
        "card-text    card-image";
  }

  .card-1 h2 {
    font-family: Georgia,'serif';
    font-size: 30px;
    font-weight: normal;
    grid-area: card-heading;
  }

  .card-1 img {
    grid-area: card-image;
    align-self: center;
  }

  .card-text {
    font-weight: 300;
    line-height: 1.4;
  }

  img {
    width: 100%;
    border-radius: 8px;
    background-size: cover;
  }

  @media (min-width: 55em) {
    .home-cards {
      grid-auto-flow: column !important;
    }
  }

  body {
    margin: 0;
    font-family: Roboto, 'sans-serif';
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
    background-color: #222029;
    padding: 24px 24px;
  }

  /* Pure CSS hamburger menu */
  /* https://codepen.io/mutedblues/pen/MmPNPG */

  /* header */

  header {
    background-color: #fff;
    box-shadow: 1px 1px 4px 0 rgba(0, 0, 0, .1);
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

  img.logo {
    height: 60px;
    width: auto;
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