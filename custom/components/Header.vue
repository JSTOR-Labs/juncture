<template>

  <div>

    <header class="header">
      <!-- <img class="logo" @click="doMenuAction({action:'load-page', path:'/'})" :src="logo"> -->
      <span class="logo" @click="doMenuAction({action:'load-page', path:'/'})">
        <img src = "https://dofe.kent-maps.online/images/dofe-logo.png" />
      </span>
      <input class="menu-btn" type="checkbox" id="menu-btn"/>
      <label class="menu-icon" for="menu-btn"><span class="navicon"></span></label>
      <ul class="menu">
        <li v-for="(navItem, idx) in nav" :key="`nav-${idx}`"@click="doMenuAction(navItem)">
          <i v-if="navItem.icon" :class="navItem.icon"></i>    {{ navItem.label }}
        </li>
      </ul>
    </header>

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

module.exports = {
  name: 'Header',
  props: {
    params: {type: Array, default: () => ([])},
    siteConfig: { type: Object, default: function(){ return {}} },
    essayConfig: { type: Object, default: function(){ return {}} },
    doActionCallback: { type: Object, default: () => ({}) }
  },
  data: () => ({
    // for contact-us email
    doActionResponse: {},
    contactName: null,
    contactEmail: null,
    contactMessage: null
  }),
  computed: {
    essayNav() { return this.params.filter(param => param.nav) },
    nav() { return this.essayNav.length > 0 ? this.essayNav : this.siteConfig.nav || [] },
    logo() { return this.essayConfig.logo || this.siteConfig.logo }
  },
  mounted() {},
  methods: {

    doMenuAction(options) {
      document.getElementById('menu-btn').checked = false // close menu
      if (options.action === 'contact-us') {
          this.showForm('contact-form')
      } else {
        this.$emit('do-action', options.action || 'load-page', options.path)
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
    doActionCallback(resp) { this.doActionResponse = resp }
  }
}

</script>

<style>

/* Pure CSS hamburger menu -  https://codepen.io/mutedblues/pen/MmPNPG */

body {
  margin: 0;
  font-family: Helvetica, sans-serif;
  background-color: #f4f4f4;
}

/* header */

.header {
  background-color: #fff;
  box-shadow: 1px 1px 4px 0 rgba(0,0,0,.1);
  position: fixed;
  width: 100%;
  z-index: 3;
}

.header ul {
  margin: 0;
  padding: 0;
  list-style: none;
  overflow: hidden;
  background-color: #fff;
  width: auto;
}

.header li {
  display: block;
  padding: 20px 20px;
  border-right: 1px solid #f4f4f4;
  text-decoration: none;
  cursor: pointer;
}

.header li svg {
  margin-right: 6px;
  min-width: 20px;
}

.header li:hover,
.header .menu-btn:hover {
  background-color: #f4f4f4;
}

.header .logo {
  display: block;
  float: left;
  font-size: 2em;
  padding: 10px 20px;
  text-decoration: none;
  cursor: pointer;
}

.logo img {
  height: 4.5vh;
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
  padding: 28px 20px;
  position: relative;
  float: right;
  user-select: none;
}

.header .menu-icon .navicon {
  background: #333;
  display: block;
  height: 2px;
  position: relative;
  transition: background .2s ease-out;
  width: 18px;
}

.header .menu-icon .navicon:before,
.header .menu-icon .navicon:after {
  background: #333;
  content: '';
  display: block;
  height: 100%;
  position: absolute;
  transition: all .2s ease-out;
  width: 100%;
}

.header .menu-icon .navicon:before {
  top: 5px;
}

.header .menu-icon .navicon:after {
  top: -5px;
}

/* menu btn */

.header .menu-btn {
  display: none;
}

.header .menu-btn:checked ~ .menu {
  max-height: 240px;
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
  .header li {
    float: left;
  }
  .header li a {
    padding: 20px 30px;
  }
  .header .menu {
    clear: none;
    float: right;
    max-height: none;
  }
  .header .menu-icon {
    display: none;
  }
}

</style>