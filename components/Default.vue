<template>
  <div id="default" :class="{'fixed-header': fixedHeader}">

    <header v-if="fixedHeader" class="header">
      <img class="logo" @click="doMenuAction({action:'load-page', path:'/'})" :src="logo">
      <input class="menu-btn" type="checkbox" id="menu-btn"/>
      <label class="menu-icon" for="menu-btn"><span class="navicon"></span></label>
      <ul class="menu">

        <template v-for="(navItem, idx) in nav">
          <li v-if="(!navItem['if-authenticated'] || isAuthenticated) && (!navItem['if-admin'] || isAdmin)" 
              :key="`nav-${idx}`"@click="doMenuAction(navItem)">
            <i v-if="navItem.icon" :class="navItem.icon"></i>{{ navItem.label }}
          </li>
        </template>

        <template v-if="isJuncture">

          <template v-if="loginsEnabled">
            <li v-if="isAuthenticated" @click="doMenuAction({action:'logout'})"><i :class="`fas fa-user`"></i>Logout</li>
            <li v-else @click="doMenuAction({action:'authenticate'})"><i :class="`fas fa-user`"></i>Login using Github</li>
          </template>

          <li @click="doMenuAction({action:'view-markdown'})"><i class="fas fa-file-code"></i>View page markdown</li>
          <li @click="doMenuAction({action:'goto-github'})"><i class="fab fa-github"></i>View on GitHub</li>

          <!-- 
          <template v-if="isAuthenticated">
            <hr>
            <li v-if="((contentSource.acct !== 'jstor-labs' && contentSource.repo !== 'juncture') || isAdmin)" @click="doMenuAction({action:'edit-page'})">
              <i class="fas fa-edit"></i>Edit this page
            </li>
            <li v-if="((contentSource.acct !== 'jstor-labs' && contentSource.repo !== 'juncture') || isAdmin)" @click="doMenuAction({action:'add-page'})">
              <i class="fas fa-file-medical"></i>Add a page
            </li>
            <li @click="doMenuAction({action:'create-site'})"><i class="fas fa-plus-circle"></i>Create new site</li>

            <template v-if="isAdmin">
              <hr>
              <li v-if="isAdmin" @click="doMenuAction({action:'software-update'})"><i class="fas fa-wrench"></i>Software update</li>
            </template>
          </template>
          -->

        </template>
        <hr>
        <li v-if="version"><div class="version">Version: {{version}}</div></li>

      </ul>
    </header>

    <section v-for="(section, sidx) in content" :key="sidx" :id="section.id || `section-${sidx}`" :class="Array.from(section.classes).join(' ')">

      <template v-if="section.classes.has('heading')">

        <header v-if="!fixedHeader" :class="`header${essayConfig['force-hamburger'] ? '' : ' responsive'}`">
          <img class="logo" @click="doMenuAction({action:'load-page', path:'/'})" :src="logo">
          <input class="menu-btn" type="checkbox" id="menu-btn"/>
          <label class="menu-icon" for="menu-btn"><span class="navicon"></span></label>
          <ul class="menu">
            <template v-if="loginsEnabled">
              <li v-if="isAuthenticated" @click="doMenuAction({action:'logout'})"><i :class="`fas fa-user`"></i>Logout</li>
              <li v-else @click="doMenuAction({action:'authenticate'})"><i :class="`fas fa-user`"></i>Login using Github</li>
            </template>
            <li v-for="navItem in nav" :key="navItem.path" @click="doMenuAction(navItem)">
              <i v-if="navItem.icon" :class="navItem.icon"></i>{{ navItem.label }}
            </li>
          </ul>
        </header>

        <div :style="section.backgroundImage ? `backgroundImage: url(${section.backgroundImage})` : ''" v-html="section.html"></div>
      </template>

      <div v-else-if="section.classes.has('footer')" v-html="section.html"></div>
      
      <template v-else>
        <h1 v-if="section.heading" v-html="section.heading"></h1>
        <div v-if="section.html" v-html="section.html"></div>          
        
        <div v-if="section.cards" :class="Array.from(section.cards.classes).join(' ')">

          <template v-if="section.cards.classes.has('carousel')">
            <div v-for="(card, idx) in section.cards.content" :key="`carousel-slide-${idx}`" class="carousel-slides fade">
              <span class="prev" @click="prevSlide">&#10094;</span>
              <div class="carousel-image" v-html="card.media"></div>
              <div class="carousel-description">
                <div class="carousel-slide-title" v-html="card.heading"></div>
                <div class="carousel-slide-description">
                  <p v-for="(para, pidx) in card.content" :key="`carousel-text-${pidx}`" :class="Array.from(para.classes).join(' ')"
                      v-html="para.html"></p>
                </div>
              </div>
              <span class="next" @click="nextSlide">&#10095;</span>
            </div>
            <div class="dots">
              <span v-for="(card, idx) in section.cards.content" :key="`carousel-dot-${idx}`" class="dot" @click="showSlide(idx)"></span>
            </div>
          </template>

          <template v-else>
            <div v-for="(card, cidx) in section.cards.content" :key="`${sidx}-${cidx}`" :id="card.id" :class="Array.from(card.classes).join(' ')">
              <div v-if="card.media" class="media" v-html="card.media"></div>
              <h2 v-if="card.heading" v-html="card.heading"></h2>
              <div v-if="card.content.length > 0" class="card-text">
                <input type="checkbox" :id="`exp-${sidx}-${cidx}`">
                <div class="clamp-wrapper">
                  <p v-for="(contentItem, ccidx) in card.content" :key="`${sidx}-${cidx}-${ccidx}`" :id="contentItem.id" 
                    :class="Array.from(contentItem.classes).join(' ')"
                    v-html="contentItem.html"
                  ></p>
                </div>
                <label :for="`exp-${sidx}-${cidx}`" role="button">more</label>
              </div>
            </div>
          </template>
        </div>

        <template v-if="section.subsections">
          <div v-for="(subsection, cidx) in section.subsections" :key="`${sidx}-${cidx}`"
            :id="subsection.id"
            :class="Array.from(subsection.classes).join(' ')" 
            v-html="subsection.html"
          ></div>
        </template>

      </template>
           
    </section>

    <div id="home-contact-form" class="modal-form" style="display: none;">
      <form v-on:submit.prevent class="form-wrapper">
        <h1>Contact us</h1>
        <input v-model="contactName" name="name" placeholder="Name" class="form-name" type="text" required>
        <input v-model="contactEmail" placeholder="Email" class="form-email" type="email" required>
        <textarea v-model="contactMessage" placeholder="Your message here" class="form-message" type="text"
                  required></textarea>
        <div v-html="doActionResponse.message"></div>
        <div class="form-controls">
          <button v-if="!doActionResponse.status" class="form-submit" @click="submitContactForm"><a>Send</a></button>
          <button v-if="!doActionResponse.status" class="form-cancel" formnovalidate @click="hideForm">Cancel</button>
          <button v-if="doActionResponse.status === 'done'" class="form-submit" @click="hideForm">Close</button>
        </div>
      </form>
    </div>

  </div>
</template>

<script>

const dependencies = []

module.exports = {
  name: 'Default',
  props: {
    html: {type: String, default: ''},
    anchor: {type: String, default: ''},
    params: {type: Array, default: () => ([])},
    isJuncture: { type: Boolean, default: false },
    isAuthenticated: { type: Boolean, default: false },
    isAdmin: { type: Boolean, default: false },
    doActionCallback: { type: Object, default: () => ({}) },
    loginsEnabled: { type: Boolean, default: false },
    contentSource: { type: Object, default: function(){ return {}} },
    siteConfig: { type: Object, default: function(){ return {}} },
    essayConfig: { type: Object, default: function(){ return {}} },
    version: {type: String, default: ''},
  },
  data: () => ({
    content: {},
    doActionResponse: {},
    contactName: '',
    contactEmail: '',
    contactMessage: '',
    slideIndex: 0,
  }),
  computed: {
    essayNav() { return this.params.filter(param => param.nav) },
    nav() {
      return this.essayNav.length > 0 ? this.essayNav : this.siteConfig.nav || []
    },
    fixedHeader() {
      return this.essayConfig['fixed-header'] === true
    },
    logo() {
      return this.essayConfig.logo || this.siteConfig.logo
    }
  },
  mounted() {
    this.loadDependencies(dependencies, 0, this.init)
    this.showSlide()
  },
  methods: {
    init() {
    },
    loadPage() {
      this.$emit('do-action', 'loadEssay', '/examples')
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
                  heading: 'h1, h2, h3, h4, h5, h6'
                }).forEach(entry => {
                  let [fld, selector] = entry
                  let found = el.querySelector(selector)
                  if (found) card[fld] = fld === 'media' ? found.outerHTML : found.innerHTML
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
                return card
              })
          }
        }
          
        if (!cards) {
          subsections = Array.from(section.querySelectorAll(':scope > section'))
            .map(el => { return { html: el.innerHTML, classes: new Set() } })
          //if (subsections.length > 0) {        
          //  content.push({classes: new Set(section.querySelector(':scope > section').className.split(' ').filter(cls => cls !== '')), sections: subsections})
          //}
        }

        let result = {
          heading: section.querySelector('h1, h2, h3, h4, h5, h6').innerHTML,
          classes, 
          html
        }
        if (section.id) result.id = section.id
        if (backgroundImage) result.backgroundImage = backgroundImage.src
        if (cards) result.cards = cards
        if (subsections) result.subsections = subsections

        return result
      })
    },

    doMenuAction(options) {
      document.getElementById('menu-btn').checked = false
      if (options.action === 'load-page') {
        this.$emit('do-action', 'load-page', options.path)
      } else if (options.action === 'contact-us') {
          this.toggleContactForm()
      } else {
        this.$emit('do-action', options.action, options.path)
      }
    },

    toggleContactForm() {
      let formId = 'home-contact-form'
      if (document.getElementById(formId).style.display === 'none') this.showForm(formId)
      else this.hideForm()
    },

    showForm(formId) {
      document.getElementById('default').classList.add('dimmed')
      let form = document.getElementById(formId)
      form.style.display = 'unset'
      form.classList.add('visible-form')
    },

    hideForm() {
      document.getElementById('default').classList.remove('dimmed')
      let form = document.querySelector('.visible-form')
      form.style.display = 'none'
      form.classList.remove('visible-form')
      this.doActionResponse = {}
    },

    submitContactForm() {
      this.$emit('do-action', 'sendmail', {
        from: `${this.contactName} <${this.contactEmail}>`,
        to: this.siteConfig.contactForm.to,
        subject: this.siteConfig.contactForm.subject,
        message: `${this.contactMessage}\n\r[Sent by: ${this.contactName} <${this.contactEmail}>]`
      })
    },

    // Next/previous controls
    prevSlide() {
      this.showSlide(this.slideIndex === 0 ? document.querySelectorAll('.carousel-slides').length - 1 : this.slideIndex - 1)
    },

    nextSlide(n) {
      this.showSlide(this.slideIndex < document.querySelectorAll('.carousel-slides').length - 1 ? this.slideIndex + 1 : 0)
    },

    // Thumbnail image controls
    currentSlide(n) {
      this.showSlide(n)
    },

    showSlide(n) {
      n = n || 0
      if (document.querySelector('.carousel')) {
        this.slideIndex = n
        Array.from(document.querySelectorAll('.carousel-slides'))
          .forEach((slide, idx) => {
            slide.style.display = idx === this.slideIndex ? 'grid' : 'none'
          })
        Array.from(document.querySelectorAll('.dot'))
          .forEach((dot, idx) => {
            if (idx === this.slideIndex) dot.classList.add('active-slide')
            else dot.classList.remove('active-slide')
          })
      }
    }

  },
  watch: {
    essayConfig: {
      handler: function () {
        let app = document.getElementById('app')
        Array.from(app.classList).forEach(cls => app.classList.remove(cls))
        if (this.essayConfig.class) app.classList.add(this.essayConfig.class.split(' '))
      },
      immediate: true
    },
    html: {
      handler: function (html) {
        if (html) {
          this.content = this.parseHtml(html)
          if (this.anchor) this.$nextTick(() => document.getElementById(this.anchor).scrollIntoView())
          this.$nextTick(() => {
            let root = document.getElementById('essay')
            this.convertLinks(root)
            const ps = document.querySelectorAll('.clamp-wrapper')
            const observer = new ResizeObserver(entries => {
              for (let entry of entries) {
                entry.target.classList[entry.target.scrollHeight > entry.contentRect.height ? 'add' : 'remove']('truncated')
              }
            })
            ps.forEach(p => observer.observe(p))
          })
        }
      },
      immediate: true
    },
    doActionCallback(resp) { this.doActionResponse = resp }
  }
}

</script>

<style scoped>

html {
  scroll-behavior: smooth;
}

section h1 {
  text-align: center;
  font-family: Georgia, 'serif';
  font-size: 30px;
  margin-bottom: 40px;
}

section p {
  font-size: 18px;
  font-weight: 300;
  line-height: 1.4;
}

section.center p {
  text-align: center;
}

section p.button {
  padding-top: 30px;
}

p.button a sup {
  display: none;
}

section .button a {
  color: #fff !important;
  background-color: #5B152E;
  border-radius: 50px;
  text-decoration: none;
  font-size: 24px;
  font-family: Roboto, 'sans-serif';
  padding: 12px 48px;
  box-shadow: 0 3px 40px rgb(0 0 0 / 25%);
}

.fixed-.header.header{
  position: fixed;
  top: 0;
  background-color: #5B152E;
}

.fixed-header > section:first-of-type {
  margin-top: 80px;
}

.heading .button a {
  color: #000 !important;
  background-color: #FFE55A;
  border-radius: 50px;
  text-decoration: none;
  font-size: 30px;
  font-family: Roboto, 'sans-serif';
  padding: 16px 72px;
  box-shadow: 0px 3px 40px rgba(0, 0, 0, 0.25);
}

.notification {
  font-size: 1.4em;
  font-weight: 500;
}

/************ Footer ***********/
section.footer {
  padding: 24px;
  background-color: #222029 !important;
  color: white;
}

.footer ul {
  display: grid;
  grid-auto-flow: column;
  align-items: center;
  margin: 0;
  list-style: none;
  padding-inline-start: 0;
}

@media (max-width: 48em) {
  .footer ul {
    display: block;
  }
   .footer li {
    margin-bottom: 24px;
  }
}

.footer li:not(:first-child) {
  justify-self:end;
}

.footer li a {
  color: white !important;
  text-decoration: none;
}

.footer li a sup {
  display: none;
}

.footer img {
  height: 30px;
  padding: 4px 12px;
  vertical-align: middle;
}
/************ End Footer ***********/

/************ Cards ***********/
.cards {
  display: grid;
  grid-auto-flow: row;
  gap: 1em;
}

.card {
  padding: 12px;
  display: flex;
  flex-direction: column;
}

.card h2 {
  /* margin-top: 40px; */
  margin-bottom: 0;
  font-weight: 400;
}

.card .media {
  text-align: center;
  /* min-height: 300px;*/
}

.card .media video {
  border-radius: 8px;
}

.card img {
  width: 100%;
  max-height: 300px;
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

@media (min-width: 48em) {
  .cards {
    grid-auto-flow: column !important;
    grid-auto-columns: 1fr;
  }
}

@media (max-width: 48em) {
  #about .horizontal .card {
    display: block;
  }

  #about .horizontal .card .media {
    margin-bottom: 40px;
  }
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

/************ Memu ***********/
/* Pure CSS hamburger menu -  https://codepen.io/mutedblues/pen/MmPNPG */

/* header */

#default {
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: relative;
  color: black;
}

section {
  padding: 72px 24px;
  background-color: white;
}

section:nth-child(odd) {
  background-color: #F5F5F5;
}

section h1 {
  text-align: center;
  font-family: Georgia, 'serif';
  font-size: 30px;
  margin-bottom: 40px;
}

section.heading {
  display: grid;
  grid-template-rows: 58px 1fr;
  padding: 0;
  min-height: 400px;
}

section.heading header {
  grid-area: 1 / 1 / 2 / 2;
}

section.heading > div {
  grid-area: 1 / 1 / 3 / 2;
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
  background-color: #5B152E;
  color: white;
}

section.heading p {
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

@media (max-width: 48em) {
  section.heading p {
    font-size: 2em;
  }
  .button a {
    font-size: 24px !important;
    padding: 8px 48px !important;
  }
}

.header {
  background-color: #5B152E;
  box-shadow: 1px 1px 4px 0 rgba(0,0,0,.1);
  width: 100%;
  z-index: 3;
}

.fixed-header .header {
  background-color: #5B152E;
  position: fixed;
  height: 80px;
}
.header, .header ul, .header li {
  background-color: transparent;
  color: white;
  border-right: none;
}
.fixed-header .header, .fixed-header .header ul, .fixed-header .header li {
  background-color: #5B152E;
  color: white;
  border-right: none;
}
.header ul {
  float: right;
  margin: -26px 0 0 0;
  padding: 0;
  list-style: none;
  overflow: hidden;
  filter: brightness(125%);
}

.header li {
  display: block;
  padding: 10px 20px;
  /* border-right: 1px solid #f4f4f4; */
  text-decoration: none;
  cursor: pointer;
}

.header li:hover {
  text-decoration: underline;
  filter: brightness(150%);
}

.header li svg {
  margin-right: 6px;
  min-width: 20px;
}

.header li a:hover,
.header .menu-btn:hover {
  background-color: #f4f4f4;
}

.header .logo {
  display: block;
  float: left;
  font-size: 2em;
  padding: 16px 36px;
  text-decoration: none;
  cursor: pointer;
}

img.logo {
  height: 48px;
  width: auto;
}

.version {
  font-size: 0.9rem;
  font-weight: 300;
}

/* menu */

.header .menu {
  clear: both;
  max-height: 0;
  transition: max-height .2s ease-out;
}

/* menu icon */

.header .menu-icon {
  cursor: pointer;
  display: inline-block;
  float: right;
  padding: 40px 36px;
  position: relative;
  user-select: none;
}

.header .menu-icon .navicon {
  background: #fff;
  display: block;
  height: 4px;
  border-radius: 2px;
  position: relative;
  transition: background .2s ease-out;
  width: 32px;
}

.header .menu-icon .navicon:before,
.header .menu-icon .navicon:after {
  background: #fff;
  content: '';
  display: block;
  height: 100%;
  position: absolute;
  transition: all .2s ease-out;
  width: 100%;
  border-radius: 2px;
}

.header .menu-icon .navicon:before {
  top: 10px;
}

.header .menu-icon .navicon:after {
  top: -10px;
}

/* menu btn */

.header .menu-btn {
  display: none;
}

.header .menu-btn:checked ~ .menu {
  /* max-height: 240px; */
  max-height: unset
}

.header .menu-btn:checked ~ .menu-icon .navicon {
  background: transparent;
}

.header .menu-btn:checked ~ .menu-icon .navicon:before {
  transform: rotate(-45deg);
}

.header .menu-btn:checked ~ .menu-icon .navicon:after {
  transform: rotate(45deg);
}

.header .menu-btn:checked ~ .menu-icon:not(.steps) .navicon:before,
.header .menu-btn:checked ~ .menu-icon:not(.steps) .navicon:after {
  top: 0;
}

/* 48em = 768px */
@media (min-width: 48em) {
  header.header.responsive li {
    float: left;
    padding: 20px 20px;
  }
  header.header.responsive ul {
    margin: 0;
  }
  header.header.responsive li a {
    padding: 20px 30px;
  }
  header.header.responsive .menu {
    clear: none;
    float: right;
    max-height: none;
  }
  header.header.responsive .menu-icon {
    display: none;
  }
}
/************ End Memu ***********/

/************ Carousel ***********/
.carousel {
  position: relative;
  margin: auto;
  padding: 0 30px;
}

.carousel .dots {
  text-align: center;
  margin-top: 20px;
}

.carousel-slide-title {
  font-family: Georgia, 'serif';
  font-size: 30px;
  font-weight: normal;
  text-align: left;
  padding: 2%;
}

.carousel-slide-description {
  font-weight: 300;
  line-height: 1.4;
  padding: 2%;
}

.carousel-image {
  border-radius: 8px;
  margin: 0 16px;
  background-size: cover;
}

.carousel-image img {
  border-radius: 7px;
  width: 100%;
  border: 1px solid #8a8a8a;
}

/* Hide the images by default */
.carousel-slides {
  display: grid;
  gap: 1.8em;
  grid-template-columns: 1fr 1fr;
  grid-template-areas:
    "carousel-image carousel-description";
}

@media (max-width: 48em) {
  .carousel-slides {
    grid-template-columns: unset;
    grid-template-areas: unset;
  }

  .carousel .button {
    margin-top: 24px !important ;
    text-align: center !important;
  }
}

/* Next & previous buttons */
.prev, .next {
  cursor: pointer;
  position: absolute;
  top: 50%;
  width: auto;
  margin-top: -22px;
  padding: 16px 10px;
  color: #0164b9;
  font-weight: bold;
  font-size: 32px;
  transition: 0.6s ease;
  user-select: none;
  background-color: rgba(124, 124, 124, 0.06);
}

.prev:hover, .next:hover {
  background-color: rgba(124, 124, 124, 1);
}

.next {
  right: 0;
  border-radius: 3px 0 0 3px;
}

.prev {
  left: 0;
  border-radius: 0 3px 3px 0;
}

.carousel .button {
  margin-top: 60px;
  text-align: left;
}

.carousel .button a {
  color: #fff !important;
  background-color: #5B152E;
  border-radius: 50px;
  text-decoration: none;
  font-size: 24px;
  font-family: Roboto, 'sans-serif';
  padding: 12px 48px;
  box-shadow: 0 3px 40px rgba(0, 0, 0, 0.25);
}

.carousel .button a:hover {
  background-color: #290312;
  box-shadow: 0 3px 40px rgba(0, 0, 0, 0.4); ;
}

/* The dots/bullets/indicators */
.dot {
  cursor: pointer;
  height: 15px;
  width: 15px;
  margin: 0 8px;
  background-color: #aeaeae;
  border-radius: 50%;
  display: inline-block;
  transition: background-color 0.2s ease;
}

.active-slide, .dot:hover {
  cursor: pointer;
  background-color: #5b152e;
}

/* Fading animation */
.fade {
  -webkit-animation-name: fade;
  -webkit-animation-duration: 1.5s;
  animation-name: fade;
  animation-duration: 1.5s;
}
/************ End Carousel ***********/

</style>
