
<template>
  <div ref="header" id="header" class="header" :style="containerStyle">
    <nav>
      <div id="menuToggle">
        <input type="checkbox" />
        <span></span>
        <span></span>
        <span></span>
        <ul id="menu">
          <li @click="nav('/')">
            <i :class="`fas fa-home`"></i>Home
          </li>
          <template v-for="item in siteConfig.nav">
            <li :key="item.path" @click="nav(item.path)">
              <i :class="`fas fa-${item.icon}`"></i>{{item.label}}
            </li>
          </template>
          <li @click="nav('viewMarkdown')">
            <i class="fas fa-file-code"></i>View page markdown
          </li>
        </ul>
      </div>
    </nav>

    <div class="title-bar">
      <div class="title" v-html="title"></div>
      <div class="author" v-html="author"></div>
    </div>

  </div>
</template>

<script>
  const defaultBanner = 'https://picsum.photos/id/403/1000/400?blur=1'

  module.exports = {
    name: 've-header',
    props: {
      active: { type: Boolean, default: true },
      scrollTop: { type: Number, default: 0 },
      essayConfig: { type: Object, default: () => ({}) },
      siteConfig: { type: Object, default: () => ({}) }
    },    
    data: () => ({
      dependencies: [],
    }),    
    computed: {
      containerStyle() { return { 
        height: this.active ? `${this.scrollTop < 400 ? 400 - this.scrollTop : 0}px` : '0',
        backgroundColor: 'white',
        backgroundImage: `url(${this.essayConfig.banner || this.siteConfig.banner || defaultBanner})`
      } },
      banner() { return this.essayConfigLoaded ? (this.essayConfig.banner || this.siteConfig.banner) : null },
      bannerHeight() { return this.essayConfig && this.essayConfig.bannerHeight || this.siteConfig.bannerHeight || 400 },
      title() { return this.essayConfig.title || this.siteConfig.title },
      author() { return this.essayConfig.author || this.siteConfig.tagline },
    },
    mounted() { this.loadDependencies(this.dependencies, 0, this.init) },
    methods: {
      nav(item) {
        document.querySelector('#menuToggle input').checked = false // close drawer
        this.$emit('menu-item-clicked', item)
      }
    },
    watch: {
      siteConfig: {
        handler: function (config) { console.log(`${this.$options.name}.siteConfig`, config) },
        immediate: true
      },
      essayConfig: {
        handler: function (config) { console.log(`${this.$options.name}.essayConfig`, config) },
        immediate: true
      },
      scrollTop: {
        handler: function (scrollTop) { 
          // console.log(`${this.$options.name}.scrollTop`, scrollTop) 
        },
        immediate: true
      }
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
    font-size: min(8vw, 2em);
    margin: 0 0 0 22px;
    padding: 22px 0 0 50px;
  }
  .author {
    grid-area: author;
    font-size: min(6vw, 1.3em);
    margin: 0 0 0 22px;
    padding: 0 0 6px 50px;
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
    margin-top: 6px;
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

  .app-version {
    font-size: 0.9rem;
  }

  .subtitle {
    font-size: 1.1rem;
    font-weight: bold;
  }

</style>