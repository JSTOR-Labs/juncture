
<template>
  <div ref="header" id="header-component" class="header" :style="containerStyle">
    
    <nav>
      <div id="menuToggle">
        <input type="checkbox" />
        <span></span>
        <span></span>
        <span></span>
        <ul id="menu">

          <li @click="doMenuAction({action:'load-page', path:'/'})"><i :class="`fas fa-home`"></i>Home</li>

          <!--  Adds menu items defined in site config.yaml -->
          <template v-for="(navItem, idx) in siteConfig.nav">
            <li :key="`nav-${idx}`" @click="doMenuAction(navItem)">
              <i v-if="navItem.icon" :class="navItem.icon"></i>{{ navItem.label }}
            </li>
          </template>

          <template v-if="isJuncture">
            <hr>

            <li v-if="loginsEnabled">
              <a v-if="isAuthenticated" @click="doMenuAction({action:'logout'})"><i :class="`fas fa-user`"></i>Logout</a>
              <a v-else @click="doMenuAction({action:'authenticate'})"><i :class="`fas fa-user`"></i>Login</a>
            </li>

            <li @click="doMenuAction({action:'user-guide'})"><i class="far fa-file-alt"></i>Juncture User Guide</li>

            <template v-if="isAuthenticated">
              <li @click="doMenuAction({action:'view-markdown'})"><i class="fas fa-file-code"></i>View page markdown</li>
              <!--
              <li v-if="((contentSource.acct !== 'jstor-labs' && contentSource.repo !== 'juncture') || isAdmin)" @click="doMenuAction({action:'edit-page'})">
                <i class="fas fa-edit"></i>Edit this page
              </li>
              <li v-if="((contentSource.acct !== 'jstor-labs' && contentSource.repo !== 'juncture') || isAdmin)" @click="doMenuAction({action:'add-page'})">
                <i class="fas fa-file-medical"></i>Add a page
              </li>
              -->
              <li @click="doMenuAction({action:'goto-github'})"><i class="fab fa-github"></i>View on GitHub</li>
                          
              <hr>
              <!--
              <li v-if="isAuthenticated" @click="doMenuAction({action:'create-site'})"><i class="fas fa-plus-circle"></i>Create new site</li>
              <li v-if="isAdmin" @click="doMenuAction({action:'software-update'})"><i class="fas fa-wrench"></i>Software update</li>
              -->
            </template>

          </template>

          <li v-if="version"> <br><div class="version">Version: {{version}}</div></li>
        </ul>
      </div>
    </nav>

    <template v-if="path === '/'">

      <div class="title-bar">
        <div class="title" v-html="title"></div>
        <div class="author" v-html="author || tagline"></div>
      </div>
    
    </template>

    <template v-else>

      <div class="title-bar">
        <div class="title" v-html="title"></div>
        <div class="author" v-html="author || tagline"></div>
      </div>
    
    </template>

    <div id="contact-form" class="modal-form" style="display: none;">
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
  const defaultBanner = 'https://picsum.photos/id/403/1000/400?blur=1'

  module.exports = {
    name: 've-header',
    props: {
      viewerIsActive: { type: Boolean, default: true },
      path: { type: String, default: '/' },
      scrollTop: { type: Number, default: 0 },
      essayConfig: { type: Object, default: () => ({}) },
      siteConfig: { type: Object, default: () => ({}) },
      isJuncture: { type: Boolean, default: false },
      isAuthenticated: { type: Boolean, default: false },
      isAdmin: { type: Boolean, default: false },
      doActionCallback: { type: Object, default: () => ({}) },
      loginsEnabled: { type: Boolean, default: false },
      contentSource: { type: Object, default: () => ({}) },
      version: { type: String, default: '' },
    },    
    data: () => ({
      dependencies: [],
      doActionResponse: {},

      // for contact-us email
      contactName: null,
      contactEmail: null,
      contactMessage: null
    }),    
    computed: {
      containerStyle() { return { 
        height: this.viewerIsActive ? `${this.scrollTop < 400 ? 400 - this.scrollTop : 0}px` : '0',
        backgroundColor: 'white',
        backgroundImage: `url(${this.banner})`
      } },
      banner() { return this.essayConfig !== null ? (this.essayConfig.banner || this.siteConfig.banner || 'https://picsum.photos/id/857/1000/400') : null },
      title() { return this.essayConfig !== null ? this.essayConfig.title || this.siteConfig.title : 'Juncture'},
      tagline() { return this.essayConfig !== null ? this.siteConfig.tagline : null },
      author() { return this.essayConfig !== null ? this.essayConfig.author : null },
    },
    mounted() { this.loadDependencies(this.dependencies, 0, this.init) },
    methods: {

      doMenuAction(options) {
        document.querySelector('#menuToggle input').checked = false
        if (options.action === 'load-page') {
          this.$emit('do-action', 'load-page', options.path)
        } else if (options.action === 'contact-us') {
          this.showForm('contact-form')
        } else {
          this.$emit('do-action', options.action, options.path)
        }
      },

      showForm(formId) {
        document.getElementById('app').classList.add('dimmed')
        let form = document.getElementById(formId)
        form.style.display = 'unset'
        form.classList.add('visible-form')
      },

      hideForm() {
        document.getElementById('app').classList.remove('dimmed')
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
      }

    },
  
    watch: {
      doActionCallback(resp) { this.doActionResponse = resp },
    }
  }
</script>

<style scoped>

  [v-cloak] { display: none; }

  body {
    margin: 0;
    padding: 0;
    background-color: white;
    color: #444;
  }

  .header {
    font-family: Roboto, sans-serif;
    font-size: 1rem;
    min-height: 90px;
    height: 400px;
    background-repeat: no-repeat;
    background-position: center center;
    background-size: cover;
    position: relative;
    margin: 0;
    color: #444;
  }

  .title-bar {
    display: grid;
    align-items: stretch;
    grid-template-columns: 1fr;
    grid-template-rows: 1fr 1fr;
    grid-template-areas: 
      "title"
      "author";
    color: white;
    background-color: rgba(0, 0, 0, .6);
    /* padding-top: 14px; */
    position: absolute;
    top: calc(100% - 100px);
    height: 100px;
    width: 100%;
    font-weight: bold;
  }

  .title {
    grid-area: title;
    font-size: min(8vw, 2.2em);
    margin: 0 0 0 22px;
    padding: 22px 0 0 50px;
  }
  .author {
    grid-area: author;
    font-size: min(6vw, 1.3em);
    margin: 0 0 0 22px;
    padding: 0 0 6px 50px;
    align-self: center;
  }

  #menuToggle a {
    text-decoration: none;
    color: #232323;
    transition: color 0.3s ease;
  }

  #menuToggle a:hover {
    color: tomato;
  }

  #menuToggle input {
    display: block;
    width: 40px;
    height: 32px;
    position: absolute;
    top: -7px;
    left: -5px;
    cursor: pointer;
    opacity: 0; /* hide this */
    z-index: 2; /* and place it over the hamburger */
    -webkit-touch-callout: none;
  }

  /*
  * Just a quick hamburger
  */
  #menuToggle span {
    display: block;
    width: 30px;
    height: 4px;
    margin-bottom: 4px;
    position: relative;
    background: #cdcdcd;
    border-radius: 3px;
    z-index: 1;
    transform-origin: 4px 0px;
    transition: transform 0.5s cubic-bezier(0.77,0.2,0.05,1.0),
                background 0.5s cubic-bezier(0.77,0.2,0.05,1.0),
                opacity 0.55s ease;
  }

  #menuToggle span:first-child {
    transform-origin: 0% 0%;
  }

  #menuToggle span:nth-last-child(2) {
    transform-origin: 0% 100%;
  }

  /* 
  * Transform all the slices of hamburger
  * into a crossmark.
  */
  #menuToggle input:checked ~ span {
    opacity: 1;
    transform: rotate(45deg) translate(-2px, -1px);
    background: #232323;
  }

  /*
  * But let's hide the middle one.
  */
  #menuToggle input:checked ~ span:nth-last-child(3) {
    opacity: 0;
    transform: rotate(0deg) scale(0.2, 0.2);
  }

  /*
  * Ohyeah and the last one should go the other direction
  */
  #menuToggle input:checked ~ span:nth-last-child(2) {
    transform: rotate(-45deg) translate(0, -1px);
  }

  /*
  * Make this absolute positioned
  * at the top left of the screen
  */
  #menu {
    position: absolute;
    width: 230px;
    margin: -100px 0 0 -50px;
    padding: 120px 50px 10px 45px;
    background: #ededed;
    list-style-type: none;
    -webkit-font-smoothing: antialiased;
    /* to stop flickering of text in safari */
    transform-origin: 0% 0%;
    transform: translate(-100%, 0);
    transition: transform 0.5s cubic-bezier(0.77,0.2,0.05,1.0);
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
  }

  #menu li {
    display: flex;
    padding: 0.5em 0;
    font-size: 1.1em;
    color: #333;
  }

  #menu li i {
    width: 20px;
    margin-right: 10px;
    text-align: center;
  }

  #menu li:hover {
    cursor: pointer;
    color: #1976d2;
  }

  #menu li svg {
    min-width: 1.5em;
    margin-right: 10px;
    /* margin-top: 6px; */
    /* font-weight: bold; */
    font-size: 1em;
  }

  /*
  * And let's slide it in from the left
  */
  #menuToggle input:checked ~ ul {
    transform: none;
  }

  #menuToggle {
    display: block;
    position: relative;
    top: 20px;
    /*left: 30px;*/
    margin-left: 20px;
    z-index: 1;
    -webkit-user-select: none;
    user-select: none;
  }

  .version {
    font-size: 0.9rem;
  }

  .subtitle {
    font-size: 1.1rem;
    font-weight: bold;
  }

</style>