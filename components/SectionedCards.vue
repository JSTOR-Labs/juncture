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

    <section v-for="(section, sidx) in content" :key="sidx" :class="section.classes.join(' ')">

      <template v-if="section.classes.has('heading')">
        <header v-if="!fixedHeader">
          <img class="logo" @click="doMenuAction('loadEssay', '/')" :src="logo">
          <input class="menu-btn" type="checkbox" id="menu-btn" />
          <label class="menu-icon" for="menu-btn"><span class="navicon"></span></label>
          <ul class="menu">
            <li v-for="navItem in nav" :key="navItem.path" @click="doMenuAction('loadEssay', navItem.path)">
              <i v-if="navItem.icon" :class="navItem.icon"></i>{{navItem.label}}
            </li>
          </ul>
        </header>
        <div class="card-text" :style="`backgroundImage: url(${section.backgroundImage})`">
          <p v-for="(para, pidx) in section.cards[0].content" :key="pidx" :class="para.classes.join(' ')" v-html="para.text"></p>
        </div>
      </template>


      <template v-else-if="section.classes.has('carousel')">
        <div class="slideshow-container">
          <h1 v-if="section.heading" v-html="section.heading"></h1>
          <div v-for="(card, idx) in section.cards" :key="`carousel-image-${idx}`" class="mySlides fade">
            <a class="prev" @click="plusSlides(-1)">&#10094;</a>
            <div class="float-child">
              <img class="slideshow-img" :src="card.image">
            </div>
            <div class="float-child">
              <div class="slideshow-title" v-html="card.heading"></div>
              <div class="slideshow-description">
                <p v-for="(para, pidx) in card.content" :key="`carousel-text-${pidx}`" :class="para.classes.join(' ')" v-html="para.text"></p>
              </div>
            </div>
            <a class="next" @click="plusSlides(1)">&#10095;</a>
          </div>

           <br>
          <!-- The dots/circles -->
          <div style="position: absolute; bottom: 0; right: 47%;">
            <span v-for="(card, idx) in section.cards" :key="`carousel-dot-${idx}`" class="dot" @click="currentSlide(idx)"></span>
          </div>
        </div>
      </template>

      <template v-else-if="section.classes.has('footer')">
        <div v-html="section.content"></div>
      </template>

      <template v-else>
        <h1 v-if="section.heading" v-html="section.heading"></h1>
        <div class="home-cards">
          <div v-for="(card, cidx) in section.cards" :key="`${sidx}-${cidx}`" 
              :class="`${section.cards.length === 1 ? 'card-1' : 'card-n'}`">
            <img v-if="card.image" :src="card.image">
            <h2 v-if="card.heading" v-html="card.heading"></h2>
            <div class="card-text">
              <p v-for="(para, pidx) in card.content" :key="`${sidx}-${cidx}-${pidx}`" :class="para.classes.join(' ')" v-html="para.text"></p>
            </div>
          </div>
        </div>
        </template>
      </section>  


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

const dependencies = ['https://cdnjs.cloudflare.com/ajax/libs/Glide.js/3.2.0/glide.min.js',
'https://cdnjs.cloudflare.com/ajax/libs/Glide.js/3.0.2/css/glide.core.css',
'https://cdnjs.cloudflare.com/ajax/libs/Glide.js/3.0.2/css/glide.theme.css']

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
      console.log('loadPage')
      //this.showSlides(this.slideIndex);
      this.$emit('do-action', 'loadEssay', '/examples')
    },

    // Creates content object from input HTML
    parseHtml(html) {
      let root = new DOMParser().parseFromString(html, 'text/html').children[0].children[1]
      console.log(root)
      return Array.from(root.querySelectorAll(':scope > section')).map(section => {
        console.log(section)
        let backgroundImage = section.querySelector('p.background-image > img')
        let classes = new Set(section.classList)
        console.log(classes)
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
                heading: 'h1, h2, h3, h4, h5, h6'
              }).forEach(entry => {
                let [fld, selector] = entry
                let found = el.querySelector(selector)
                if (found) card[fld] = found.tagName === 'IMG' ? found.src : found.innerHTML
              })
              card.content = Array.from(el.querySelectorAll('p'))
                .filter(p => p.textContent)
                .map(p => { return { text: p.innerHTML, id: p.id, classes: Array.from(p.classList) } })
              return card
            })
          }
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
    },

    glider(){
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
      if (n > slides.length) {this.slideIndex = 1}
      if (n < 1) {this.slideIndex = slides.length}
      for (i = 0; i < slides.length; i++) {
          slides[i].style.display = "none";
      }
      for (i = 0; i < dots.length; i++) {
          dots[i].className = dots[i].className.replace(" active", "");
      }
      slides[this.slideIndex-1].style.display = "block";
      dots[this.slideIndex-1].className += " active";
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

section.footer {
  padding: 0 !important;
}

.footer div {
  background-color: #555;
}

.footer img {
  height: 30px;
  width: auto;
  border-radius: unset;
}

.footer ul {
  display: grid;
  grid-auto-flow: column;
  align-items: center;
  justify-content: left;
  list-style-type: none;
  margin: 0 0 0 12px;
  padding: 2px 0 0 0;
  height: 48px;
}

.footer ul li {
  margin-right: 40px;
}

.footer ul li a {
  color: white !important;
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

* {box-sizing:border-box}

/* Slideshow container */
.slideshow-container {
  max-width: 95%;
  position: relative;
  margin: auto;
  padding-left: 2%;
  padding-right: 2%;
  height: 100%;
}

.slideshow-title {
  font-family: Georgia,'serif';
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

.slideshow-img {
  margin-left: 3%;
  width: 100%;
  height: 420px;
  border: 1px solid #8a8a8a;
  background-size: cover;
}

.prev-button {
  float:left;
  width:5%
}
.next-button {
  float:left;
  width:5%;
}
/* Hide the images by default */
.mySlides {
  display: flex;
}

/* Next & previous buttons */
.prev, .next {
  cursor: pointer;
  position: absolute;
  top: 50%;
  width: auto;
  margin-top: -22px;
  padding: 11px;
  color: white;
  font-weight: bold;
  font-size: 18px;
  transition: 0.6s ease;
  border-radius: 0 3px 3px 0;
  user-select: none;
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
    box-shadow: 0px 3px 40px rgba(0, 0, 0, 0.25);
  }

/* Position the "next button" to the right */
.next {
  right: 0;
  border-radius: 3px 0 0 3px;
}

/* On hover, add a black background color with a little bit see-through */
.prev:hover, .next:hover {
  background-color: rgba(116, 116, 116, 0.8);
}

.float-child{
  width: 45%;
  float: left;
  margin:2%;  
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
  margin: 0 2px;
  /*background-color: #bbb;*/
  background-color: #717171;
  border-radius: 50%;
  display: inline-block;
  transition: background-color 0.6s ease;
}

.active, .dot:hover {
  /*background-color: #717171;*/
  background-color: #bbb;
}

/* Fading animation */
.fade {
  -webkit-animation-name: fade;
  -webkit-animation-duration: 1.5s;
  animation-name: fade;
  animation-duration: 1.5s;
}

@-webkit-keyframes fade {
  from {opacity: .4}
  to {opacity: 1}
}

@keyframes fade {
  from {opacity: .4}
  to {opacity: 1}
}

</style>