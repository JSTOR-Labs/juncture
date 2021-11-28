<template>
  <div id="home" :class="{'fixed-header': fixedHeader}">

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

    <section v-for="(section, sidx) in content" :key="sidx" :id="section.id || `section-${sidx}`" :class="section.classes.join(' ')">

      <template v-if="section.classes.has('heading')">
        <header v-if="!fixedHeader">
          <img class="logo" @click="doMenuAction('loadEssay', '/')" :src="logo">
          <input class="menu-btn" type="checkbox" id="menu-btn"/>
          <label class="menu-icon" for="menu-btn"><span class="navicon"></span></label>
          <ul class="menu">
            <template v-if="loginsEnabled">
              <li v-if="isAuthenticated" @click="doMenuAction('logout')"><i :class="`fas fa-user`"></i>Logout</li>
              <li v-else @click="doMenuAction('authenticate')"><i :class="`fas fa-user`"></i>Log in using Github</li>
            </template>
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


      <template v-else-if="section.classes.has('carousel')">
        <div class="slideshow-container">
          <h1 v-if="section.heading" v-html="section.heading"></h1>
          <div v-for="(card, idx) in section.cards" :key="`carousel-image-${idx}`" class="mySlides fade">
            <a class="prev" @click="plusSlides(-1)">&#10094;</a>
            <div class="float-image">
              <img class="slideshow-img" :src="card.image">
            </div>
            <div class="float-description">
              <div class="slideshow-title" v-html="card.heading"></div>
              <div class="slideshow-description">
                <p v-for="(para, pidx) in card.content" :key="`carousel-text-${pidx}`" :class="para.classes.join(' ')"
                   v-html="para.text"></p>
              </div>
            </div>
            <a class="next" @click="plusSlides(1)">&#10095;</a>
          </div>

          <br>
          <!-- The dots/circles -->
          <div style="position: absolute; bottom: 0; right: 47%;">
            <span v-for="(card, idx) in section.cards" :key="`carousel-dot-${idx}`" class="dot"
                  @click="currentSlide(idx)"></span>
          </div>
        </div>
      </template>

      <template v-else-if="section.classes.has('footer')">
        <div style="display:grid; grid-auto-flow:column; align-items:center;">
          <div v-html="section.content"></div>
        </div>
        <div style="font-size:70%; font-weight:normal;" v-html="version"> </div>
      </template>

      <template v-else>
        <h1 v-if="section.heading" v-html="section.heading"></h1>
        <div class="home-cards">
          <div v-for="(card, cidx) in section.cards" :key="`${sidx}-${cidx}`"
               :class="`${section.cards.length === 1 ? 'card-1' : 'card-n'}`">
            <img v-if="card.image" :src="card.image">
            <div class="raw" v-if="card.raw" v-html="card.raw"></div>
            <h2 v-if="card.heading" v-html="card.heading"></h2>
            <div class="card-text">
              <p v-for="(para, pidx) in card.content" :key="`${sidx}-${cidx}-${pidx}`" :class="para.classes.join(' ')"
                 v-html="para.text"></p>
            </div>
          </div>
        </div>
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

const dependencies = ['https://cdnjs.cloudflare.com/ajax/libs/Glide.js/3.2.0/glide.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/Glide.js/3.0.2/css/glide.core.css',
  'https://cdnjs.cloudflare.com/ajax/libs/Glide.js/3.0.2/css/glide.theme.css']

module.exports = {
  name: 'SectionedCards',
  props: {
    html: {type: String, default: ''},
    anchor: {type: String, default: ''},
    params: {type: Array, default: () => ([])},
    isAuthenticated: { type: Boolean, default: false },
    doActionCallback: { type: Object, default: () => ({}) },
    loginsEnabled: { type: Boolean, default: false },
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
    slideIndex: 1,
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
    this.showSlides(this.slideIndex);
  },
  methods: {
    init() {
    },
    loadPage() {
      //this.showSlides(this.slideIndex);
      this.$emit('do-action', 'loadEssay', '/examples')
    },

    // Creates content object from input HTML
    parseHtml(html) {
      let root = new DOMParser().parseFromString(html, 'text/html').children[0].children[1]
      return Array.from(root.querySelectorAll(':scope > section')).map(section => {
        let backgroundImage = section.querySelector('p.background-image > img')
        let classes = new Set(section.classList)
        if (classes.has('raw')) {
          return {
            id: section.id, classes,
            content: Array.from(section.querySelectorAll('p, ul')).filter(el => el.textContent).map(el => el.outerHTML).join(' ')
          }
        } else {
          return {
            id: section.id,
            heading: section.querySelector('h1, h2, h3, h4, h5, h6').innerHTML,
            backgroundImage: backgroundImage ? backgroundImage.src : '',
            classes,
            cards: Array.from(section.querySelectorAll(':scope > section')).map(el => {
              let card = {}
              Object.entries({
                image: 'p img',
                raw: 'video',
                heading: 'h1, h2, h3, h4, h5, h6'
              }).forEach(entry => {
                let [fld, selector] = entry
                let found = el.querySelector(selector)
                if (found) {
                  if (fld === 'raw') card.raw = found.outerHTML
                  else card[fld] = found.tagName === 'IMG' ? found.src : found.innerHTML
                }
              })
              card.content = Array.from(el.querySelectorAll('p'))
                  .filter(p => p.textContent)
                  .map(p => {
                    return {text: p.innerHTML, id: p.id, classes: Array.from(p.classList)}
                  })
              return card
            })
          }
        }
      })
    },

    doMenuAction(action, options) {
      if (action === 'loadEssay') {
        if (options === '/contact-us') {
          this.toggleContactForm()
        } else {
          this.$emit('do-action', 'loadEssay', options)
        }
      } else {
        this.$emit('do-action', action, options)
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
      // console.log('this.siteConfig.contactForm.toEmail', this.siteConfig.contactForm.toEmail)
      let body = `${this.contactMessage}\n\r[Sent by: ${this.contactName} <${this.contactEmail}>]`

      this.$emit('do-action', 'send-email', {
        personalizations: [],
        from: {
          email: `${this.contactName}`,
          name: `<${this.contactEmail}>`
        },
        reply_to: {
          email: this.siteConfig.contactForm.toEmail
        },
        content: [{
          type: "text/html",
          value: body
        }]
      })
    },

    glider() {
      new Glide('.glide').mount()
    },

    // Next/previous controls
    plusSlides(n) {
      this.showSlides(this.slideIndex += n);
    },

    // Thumbnail image controls
    currentSlide(n) {
      this.showSlides(this.slideIndex = n);
    },

    showSlides(n) {
      var i;
      var slides = document.getElementsByClassName("mySlides");
      var dots = document.getElementsByClassName("dot");
      if (n > slides.length) {
        this.slideIndex = 1
      }
      if (n < 1) {
        this.slideIndex = slides.length
      }
      for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
      }
      for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
      }
      slides[this.slideIndex - 1].style.display = "grid";
      dots[this.slideIndex - 1].className += " active";
    }
  },
  watch: {
    html: {
      handler: function (html) {
        if (html) {
          this.content = this.parseHtml(html)
          if (this.anchor) this.$nextTick(() => document.getElementById(this.anchor).scrollIntoView())
        }
      },
      immediate: true
    }
  }
}

</script>

<style>

html {
  scroll-behavior: smooth;
}

a:hover {
  color: black !important;
}

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

#home section.heading > div {
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

@media (max-width: 48em) {
  #home section.heading p {
    font-size: 2em;
  }
  .button a {
    font-size: 24px !important;
    padding: 8px 48px !important;
  }
}

.heading header, .heading header ul, .heading header li {
  background-color: transparent;
  color: white;
  border-right: none;
}

.heading header {
  box-shadow: none;
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
  box-shadow: 0 3px 40px rgba(0, 0, 0, 0.25);
}

.button a:hover {
  background-color: #ffb55a;
  box-shadow: 0 3px 40px rgba(0, 0, 0, 0.4); ;
}

.home-cards video {
  border-radius: 8px;
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

.card-n img, .card-1 .raw {
  width: 100%;
  border-radius: 8px;
  background-size: cover;
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
  grid-column: 1/span3;
  align-items: flex-start;
  grid-template-areas:
        "card-heading card-image"
        "card-text    card-image";
}

.card-1 h2 {
  font-family: Georgia, 'serif';
  font-size: 30px;
  font-weight: normal;
  grid-area: card-heading;
}

.card-1 img, .card-1 .raw {
  grid-area: card-image;
  align-self: center;
  border-radius: 8px;
  width: 100%;
  background-size: cover;
}

.card-text {
  font-weight: 300;
  line-height: 1.4;
}

.juncture-can .home-cards {
  grid-template-columns: 1fr 1fr;
}

.juncture-documentation .home-cards {
  display: block!important;
}

.juncture-documentation .home-cards .card-1 {
  display: block!important;
}

.juncture-documentation .card-text {
  margin: auto;
}

.juncture-documentation .card-text p {
  text-align: center;
  margin: 16px 0;
}

.juncture-documentation .button a {
  color: #fff !important;
  background-color: #5B152E;
  border-radius: 50px;
  text-decoration: none;
  font-size: 24px;
  font-family: Roboto, 'sans-serif';
  padding: 12px 48px;
  box-shadow: 0 3px 40px rgba(0, 0, 0, 0.25);
}

.juncture-documentation .button a:hover {
  background-color: #290312;
  box-shadow: 0 3px 40px rgba(0, 0, 0, 0.4); ;
}

@media (min-width: 48em) {
  .home-cards {
    grid-auto-flow: column !important;
    grid-template-columns: 1fr 1fr 1fr;
  }

  .juncture-documentation .card-text p {
    margin: 40px !important;
  }
}

@media (max-width: 48em) {
  .card-1 {
    grid-template-areas:
          "card-image"
          "card-heading"
          "card-text";
    grid-template-columns: unset;
    grid-template-rows: unset;
  }

  .juncture-can .home-cards {
    grid-template-columns: unset!important;
  }

  .mySlides {
    grid-template-areas:unset !important;
  }

  .float-image, .float-image img {
    height: 300px;
    object-fit: cover;
    object-position: top;
  }

  .prev, .next {
    top: 25% !important;
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
  padding: 16px 20px;
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
  background: #ffffff;
  display: block;
  height: 2px;
  position: relative;
  transition: background .2s ease-out;
  width: 18px;
}

header .menu-icon .navicon:before,
header .menu-icon .navicon:after {
  background: #ffffff;
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

section.footer {
  color: white !important;
  align-content: center !important;
  background-color: #222029 !important;
  padding: 24px !important;
}

.footer img {
  height: 30px;
  width: auto;
  border-radius: unset;
}

.footer ul {
  display: block;
  list-style-type: none;
  padding-inline-start: 0;
}

.footer ul li {
  margin-bottom: 32px;
}

.footer ul li a {
  color: white !important;
}

.footer ul li:first-child {
  margin-bottom: 8px;
}

@media (min-width: 48em) {
  .footer ul {
    display: grid;
    grid-auto-flow: column;
    align-items: center;
    justify-content: left;
  }

  .footer ul li:first-child {
    margin-right: 8px;
    margin-bottom: 0;
  }

  .footer ul li {
    margin-right: 40px;
    margin-bottom: 0;
  }

  .footer ul li {
    margin-right: 24px;
  }

}

.wrap {
  max-width: 900px;
  margin: 0 auto;
}

.glide__slide {
  border: 1px solid black;
  line-height: 100px;
  margin: 0;
  text-align: center;
}

* {
  box-sizing: border-box
}

/* Slideshow container */
.slideshow-container {
  position: relative;
  margin: auto;
  padding-left: 2%;
  padding-right: 2%;
  height: 100%;
}

.slideshow-title {
  font-family: Georgia, 'serif';
  font-size: 30px;
  font-weight: normal;
  text-align: left;
  padding: 2%;
}

.slideshow-description {
  font-weight: 300;
  line-height: 1.4;
  padding: 2%;
}

.float-image {
  border-radius: 8px;
  margin: 0 16px;
  background-size: cover;
}

.float-image img {
  border-radius: 7px;
  width: 100%;
  border: 1px solid #8a8a8a;
}

.prev-button {
  float: left;
  width: 5%
}

.next-button {
  float: left;
  width: 5%;
}

/* Hide the images by default */
.mySlides {
  display: grid;
  gap: 1.8em;
  grid-template-areas:
    "float-image float-description";
}

/* Next & previous buttons */
.prev, .next {
  cursor: pointer;
  position: absolute;
  top: 50%;
  width: auto;
  margin-top: -22px;
  padding: 16px 10px;
  color: white;
  font-weight: bold;
  font-size: 32px;
  transition: 0.6s ease;
  user-select: none;
  background-color: rgba(124, 124, 124, 0.06);
}

.carousel .button {
  margin-top: 60px;
  text-align: left !important;
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

/* Position the "next button" to the right */
.next {
  right: 0;
  border-radius: 3px 0 0 3px;
}

.prev {
  left: 0;
  border-radius: 0 3px 3px 0;
}

/* On hover, add a black background color with a little bit see-through */
.prev:hover, .next:hover {
  background-color: rgba(124, 124, 124, 1);
}

.float-child {
  width: 45%;
  float: left;
  margin: 2%;
}

/* Caption text */
.text {
  color: #f2f2f2;
  font-size: 15px;
  padding: 8px 12px;
  position: absolute;
  bottom: 8px;
  width: 100%;
  text-align: center;
}

/* Number text (1/3 etc) */
.numbertext {
  color: #f2f2f2;
  font-size: 12px;
  padding: 8px 12px;
  position: absolute;
  top: 0;
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

.active, .dot:hover {
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

.modal-form {
  padding: 16px;
}

.form-wrapper {
  margin-top: 16px;
  margin-left: 10px;
}

.form-name, .form-email, .form-message{
    width: calc(100% - 24px);
    height: 40px;
    margin: 10px 0;
    padding: 8px;
    font-size: 1rem;
}

.form-message {
  height: 150px;
  font-size: 1rem;
}

.form-controls {
  padding: 24px;
}

.form-submit {
  margin-top: 1px;
  text-align: left !important;
  border: none;
  background: none;
  margin-bottom: 12px;
}

.form-submit a {
  color: #fff !important;
  background-color: #5B152E;
  border-radius: 50px;
  text-decoration: none;
  font-size: 20px;
  font-family: Roboto, 'sans-serif';
  padding: 10px 30px;
  box-shadow: 0 3px 40px rgba(0, 0, 0, 0.25);
}

.form-cancel {
  font-size: 20px;
  font-family: Roboto, 'sans-serif';
  border: none;
  background: none;
  text-decoration: underline;
}

@-webkit-keyframes fade {
  from {
    opacity: .4
  }
  to {
    opacity: 1
  }
}

@keyframes fade {
  from {
    opacity: .4
  }
  to {
    opacity: 1
  }
}

</style>