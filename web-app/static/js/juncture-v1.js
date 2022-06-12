const ENV = 'PROD'
const isJuncture = window.location.hostname.indexOf('juncture-digital.org') === 0
const ghToken = atob('Z2hwX05lcnV2RUYzRmx6M3o5YnFjQWZuOGpJQnJMR3lEMTNmYjYyVw==')
const qargs = window.location.href.indexOf('?') > 0 ? parseQueryString(window.location.href.split('?')[1]) : {}
const componentPrefix = 've1-'
const dirCache = {}

const contentSource = await getContentSource()
const siteConfig = await getSiteConfig()
const componentsList = await getComponentsList()
const availableViewers = []

componentsList.forEach(componentUrl => {
  let httpComponent = httpVueLoader(componentUrl)
  let componentName = `${componentPrefix}${camelToKebab(componentUrl.split('/').pop().split('.')[0])}`
  if (availableViewers.indexOf(componentName) <0) {
    availableViewers.push(componentName)
    Vue.component(componentName, httpComponent)
  }
})

Vue.directive('highlightjs', {
  deep: true,
  bind: function(el, binding) {
    let targets = el.querySelectorAll('code')
    targets.forEach((target) => {
      if (binding.value) {
        target.textContent = binding.value
      }
      hljs.highlightBlock(target)
    })
  },
  componentUpdated: function(el, binding) {
    let targets = el.querySelectorAll('code')
    targets.forEach((target) => {
      if (binding.value) {
        target.textContent = binding.value
        hljs.highlightBlock(target)
      }
    })
  }
})

let _vue = new Vue({
  el: '#app',
  data: () => ({
    actions: {},
    active: null,
    anchor: null,
    authenticatedUser: null,
    availableViewers,
    componentsList,
    contentSource,
    doActionCallback: {},
    entities: {},
    essayConfig: null,
    forceHorizontalLayout: window.matchMedia('only screen and (max-width: 1000px)').matches,
    ghToken,
    hoverItem: undefined,
    html,
    items: [],
    isJuncture,
    junctureVersion: '0.5.0',
    layouts: ['visual-essay vertical'],
    markdown: null,
    markdownViewer: null,
    mdDir: '/',
    mdPath: '',
    oauthCredsFound: false,
    params: [],
    path: '/',
    qargs,
    selectedItem: undefined,
    selectedViewer: null,
    scrollTop: 0,
    siteConfig,
    viewerData: {},
    viewerHeight: 0,
    viewersEnabled: [],
    viewerIsOpen: false
  }),
  computed: {
    headerComponent() { return this.essayConfig ? `${componentPrefix}${this.essayConfig.header || 'header'}` : null},
    mainComponent() { return this.essayConfig && this.essayConfig.main ? `${componentPrefix}${this.essayConfig.main.toLowerCase()}` : null},
    footerComponent() { return this.essayConfig ? `${componentPrefix}${this.essayConfig.footer || 'footer'}` : null},
    isAdminUser() { return ENV === 'DEV' || this.authenticatedUser !== null && (this.authenticatedUser.isAdmin || contentSource.acct === this.authenticatedUser.acct) },
    // ghToken() { return oauthAccessToken || ghUnscopedToken },
    viewerStyle() { return { 
      height: this.viewerIsOpen
        ? this.isVerticalLayout 
          ? '100%'
          : `calc(50vh - ${this.$refs.header.clientHeight/2}px)`
        : 0 
      } 
    },
    isVerticalLayout() { return !this.forceHorizontalLayout && this.layouts.indexOf('vertical') >= 0 },
    loginsEnabled() { return this.oauthCredsFound && (!this.essayConfig || !this.essayConfig['logins-disabled']) }
  },
  created() {},
  async mounted() {
    let path
    if (window.location.href.indexOf('#') > 0) {
      path = window.location.href.split('#')[0].split('/').slice(3).join('')
      let anchor = window.location.href.split('#').pop()
      if (path) this.anchor = anchor
      else path = anchor
    } else {
      path = window.location.pathname.slice(contentSource.basePath.length) || '/'
      path = path.length > 1 && path.slice(-1) === '/' ? path.slice(0,-1) : path
    }
    this.path = path
    let pathIsDir = await isDir(path, this.contentSource)
    this.mdDir = pathIsDir ? path : `/${path.split('/').filter(elem => elem).slice(0,-1).join('/')}`
    this.mdPath = pathIsDir ? path === '/' ? '/README.md' : `${path}/README.md` : `${path}.md`
    // console.log(`mdDir=${this.mdDir} mdPath=${this.mdPath}`)
    // Initialize Markdown source viewer
    this.markdown = await getGhFile(this.mdPath)
    this.markdownViewer = tippy(this.$refs.header, {
      trigger: 'manual', 
      theme: 'light-border',
      allowHTML: true,
      interactive: true,
      arrow: false,
      placement: 'bottom-start',          
      onShow: async (instance) => { instance.setContent(this.$refs.markdownViewer.innerHTML) },
      onHide: (instance) => {}
    })
    this.parseEssay()
  },
  methods: {
    authenticate() {
      let provider = new firebase.auth.GithubAuthProvider()
      provider.addScope('repo')
      firebase.auth().signInWithRedirect(provider)
    },
  
    // Handles menu actions from header
    async doAction(action, options) {
      if (action === 'sendmail') {
        this.doActionCallback = {status: 'processing', message: 'Processing request'}
        let resp = await sendmail(options)
        this.doActionCallback = {status: 'done', message: 'Email sent'}
      } else if (action === 'view-markdown') {
        this.markdownViewer.show()
      } else if (action === 'user-guide') {
        window.open('https://github.com/JSTOR-Labs/juncture/wiki', '_blank')
      } else if (action === 'edit-page') {
        this.editMarkdown()
      } else if (action === 'goto-github') {
        window.open(`https://github.com/${contentSource.acct}/${contentSource.repo}/tree/${contentSource.ref}`, '_blank')
      } else if (action === 'viewSiteOnJuncture') {
        window.location.href = `https://juncture-digital.org/${contentSource.acct}/${contentSource.repo}`
      } else if (action === 'authenticate') {
        this.authenticate()
      } else if (action === 'logout') {
        this.logout()
      } else if (action === 'load-page') {
        let newPage = `${this.contentSource.baseUrl}${this.contentSource.basePath}${options}`
        if (this.qargs.ref) newPage += `?ref=${this.qargs.ref}`
        location.href = newPage
      }
    },

    logout() {
      console.log('logout')
    },

    // Updates viewer data from events emitted when viewer components are loaded
    updateComponentData(data) { this.viewerData = {...this.viewerData, ...data }},

    // Sets active element based on essay window scroll position
    onScroll: _.throttle(function (e) {
      e.preventDefault()
      e.stopPropagation()
      this.scrollTop = e.target.scrollTop
    }, 5),
    scroll() {},
    scrollToAnchor() {},

    parseSection(section, id) {
      let sectionCtr = 0
      let segCtr = 0
      if (section.classList.contains('cards') && !section.classList.contains('wrapper')) {
        section.classList.remove('cards')
        let wrapper = document.createElement('section')
        wrapper.className = 'cards wrapper'
        Array.from(section.querySelectorAll(':scope > section')).forEach(sec => {
          sec.classList.add('card')
          wrapper.appendChild(sec)
          // section.removeChild(sec)
        })
        section.appendChild(wrapper)
      }

      Array.from(section.children).forEach(el => {
        if (el.tagName === 'SECTION') {
          let dataId = `${id}.${++sectionCtr}`
          el.setAttribute('data-id', dataId)
          this.parseSection(el, dataId)
        } else if (el.tagName === 'P' || el.tagName === 'UL' || el.tagName === 'OL') {
          let params = []
          Array.from(el.querySelectorAll(':scope > param')).forEach(param => {
            params.push(param)
            el.removeChild(param)
          })
          let content = el.innerHTML.trim()
          if (content) {
            let seg = document.createElement('div')
            let dataId = `${id}.${++segCtr}`
            seg.setAttribute('data-id', dataId)
            seg.setAttribute('id', dataId)
            seg.classList.add('segment')
            seg.innerHTML = el.outerHTML
            params.forEach(param => seg.append(param))
            el.replaceWith(seg)
          } else {
            params.forEach(param => section.insertBefore(param, el))
            section.removeChild(el)
          }
        }
      })
    },

    /*
    if (elClasses.indexOf('cards') >= 0) {
      let wrapper = new DOMParser().parseFromString(`<section class="${elClasses.join(' ')}"></section>`, 'text/html').children[0].children[1].children[0]
      currentSection.appendChild(wrapper)
    } else {
      currentSection.classList.add(...elClasses)
      let wrapper = parent.querySelector(':scope > .cards')
      if (wrapper) {
        currentSection.classList.add('card')
        parent = wrapper
      }
    }
    */
  
    async parseEssay() {
      let tmp = new DOMParser().parseFromString(this.html, 'text/html').children[0].children[1]
      this.convertResourceUrls(tmp)

      Array.from(tmp.querySelectorAll('param'))
      .filter(param => Object.values(param.attributes).find(attr => attr.nodeName !== 'id' && attr.nodeName !== 'class') === undefined)
      .forEach(param => {
        if (param.id || param.className) {
          let prior = param.previousElementSibling
          if (param.id && prior) prior.id = param.id
          if (param.className) {
            if (prior) prior.className = param.className
            else essay.className = param.className
          }
          param.parentElement.removeChild(param)
        }
      })
  
      this.parseSection(tmp.children[0], '1')
      this.params = Array.from(tmp.querySelectorAll('param')).map((param,idx) => {
        let paramObj = { ...{
          id: `P${idx+1}`, 
          path: getDomPath(param.parentElement).filter(elem => elem !== 'html' && elem !== 'body').join('>')
          },
          ...attrsToObject(param)
        }
        let viewerTag = Object.keys(paramObj)
          .filter(attr => attr.indexOf('ve') === 0)
          .map(attr => attr.replace(/^ve-/,componentPrefix))
          .find(attr => this.availableViewers.indexOf(attr) >= 0)
        if (viewerTag) paramObj.viewer = viewerTag        
        return paramObj
      })
      this.entities = await this.getEntityData(this.findEntities(tmp, this.params))
      this.html = tmp.outerHTML
      let essayConfig = this.params.find(param => param['ve-config'])
      if (essayConfig.banner) essayConfig.banner = convertURL(essayConfig.banner, this.mdDir)
      essayConfig.header = essayConfig.header || 'header'
      essayConfig.main = essayConfig.main || essayConfig.component || 'visual-essay'
      essayConfig.footer = essayConfig.footer || 'footer'
      this.essayConfig = essayConfig

    },

    // Finds all entity references in param tags
    findEntities(root, params) {

      let entities = Object.fromEntries(
        params.filter(param => param.eid || param['ve-entity'] !== undefined)
        .map(entity => { return {...entity, ...{
          id: entity.eid || entity.id, 
          aliases: new Set(entity.aliases ? entity.aliases.split('|') : []),
          foundIn: new Set()
        }} })
        .map(entity => [entity.id, entity]))
      
      Array.from(root.querySelectorAll('span'))
        .filter(el => el.attributes.eid)
        .map(el => attrsToObject(el))
        .map(entity => { return {...entity, ...{id: entity.eid || entity.id} } })
        .forEach(entity => { if (!entities[entity.eid]) entities[entity.eid] = entity })

      params.filter(param => param.center && isEntityID(param.center))
        .map(param => { return {...param, ...{id: param.center, eid: param.center} } })
        .forEach(entity => { if (!entities[entity.eid]) entities[entity.eid] = entity })

      return entities
    },

    // Gets labels, aliases, images and geo coords for referenced Wikdata entities
    async getEntityData(entities) {
      let values = Object.values(entities).filter(entity => entity.eid).map(entity => `(<http://www.wikidata.org/entity/${entity.eid}>)`).join(' ')
      let query = `SELECT ?item ?label ?aliases ?description ?images ?coords ?whosOnFirst WHERE {
                      VALUES (?item) { ${values} }
                      ?item rdfs:label ?label . FILTER(LANG(?label) = 'en')
                      OPTIONAL { ?item schema:description ?description . FILTER(LANG(?description) = 'en') }
                      OPTIONAL { ?item skos:altLabel ?aliases . FILTER(LANG(?aliases) = 'en') }
                      OPTIONAL { ?item wdt:P18 ?images . }
                      OPTIONAL { ?item wdt:P625 ?coords . }
                      OPTIONAL { ?item wdt:P6766 ?whosOnFirst . }
                    }`
      let resp = await fetch('https://query.wikidata.org/sparql', {
        method: 'POST', body: `query=${encodeURIComponent(query)}`, 
        headers: { Accept: 'application/sparql-results+json', 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      resp = await resp.json()
      // let enrichedEntities = {}
      resp.results.bindings.forEach(rec => {
        let eid = rec.item.value.split('/').pop()
        if (!entities[eid].images) entities[eid] = {
            ...entities[eid], 
            ...{
              eid, 
              label: rec.label.value, 
              aliases: new Set(entities[eid].aliases ? Array.from(entities[eid].aliases) : []),
              description: rec.description && rec.description.value,
              geojson: rec.whosOnFirst && rec.whosOnFirst.value && this.whosOnFirstUrl(rec.whosOnFirst.value),
              images: [],
              thumbnails: [],
              coords: rec.coords && rec.coords.value.replace(/Point\(/,'').replace(/\)/,'').split(' ').reverse().map(coord => parseFloat(coord)),
              foundIn: new Set(),
            }
          }
        if (rec.aliases && !entities[eid].aliases.has(rec.aliases.value)) entities[eid].aliases.add(rec.aliases.value)
        if (rec.images && entities[eid].images.indexOf(rec.images.value) < 0) {
          entities[eid].images.push(rec.images.value)
          entities[eid].thumbnails.push(this.commonsImageUrl(rec.images.value, 200))
        }
      })
      query = `SELECT ?item ?mwPage WHERE {
                  VALUES (?item) { ${values} }
                  ?mwPage schema:about ?item .
                  ?mwPage schema:isPartOf <https://en.wikipedia.org/> . }`
      resp = await fetch('https://query.wikidata.org/sparql', {
        method: 'POST', body: `query=${encodeURIComponent(query)}`, 
        headers: { Accept: 'application/sparql-results+json', 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      resp = await resp.json()
      resp.results.bindings.forEach(rec => entities[rec.item.value.split('/').pop()]['mwPage'] = rec.mwPage.value)
      return entities
    },

    convertResourceUrls(root) {
      root.querySelectorAll('img').forEach(img => {
        if (img.src.indexOf(window.location.origin) === 0) img.setAttribute('src', convertURL(img.src, this.mdDir))
      })
      root.querySelectorAll('param').forEach(param => {
        ['url', 'banner', 'article', 'logo'].forEach(attr => {
          if (param.attributes[attr]) {
            param.setAttribute(attr, convertURL(param.attributes[attr].value, this.mdDir))
          }
        })
      })
      return root
    },

    // Creates a GeoJSON file URL from a Who's on First ID 
    whosOnFirstUrl(wof) {
      let wofParts = []
      for (let i = 0; i < wof.length; i += 3) {
        wofParts.push(wof.slice(i,i+3))
      }
      return `https://data.whosonfirst.org/${wofParts.join('/')}/${wof}.geojson`
    },
    
    commonsImageUrl(url, width) {
      // Converts Wikimedia commons File URL to an image link
      //  If a width is provided a thumbnail is returned
      let mwImg = url.indexOf('Special:FilePath') > 0 ? url.split('/Special:FilePath/').pop() :  url.split('/File:').pop()
      mwImg = decodeURIComponent(mwImg).replace(/ /g,'_')
      const ImgMD5 = md5(mwImg)
      const extension = mwImg.slice(mwImg.length-4)
      let imgUrl = `https://upload.wikimedia.org/wikipedia/commons/${width ? 'thumb/' : ''}`
      imgUrl += `${ImgMD5.slice(0,1)}/${ImgMD5.slice(0,2)}/${mwImg}`
      if (width) imgUrl += `/${width}px-${mwImg}`
      if (extension === '.svg') imgUrl += '.png'
      if (extension === '.tif') imgUrl += '.jpg'
      return imgUrl
    },

    addItemEventHandlers(elem) {
      elem.querySelectorAll('.inferred').forEach((entity) => {
        entity.addEventListener('click', this.itemClickHandler)
        entity.addEventListener('mouseover', this.setHoverItem)
        entity.addEventListener('mouseout', this.setHoverItem)
      })
    },
    removeItemEventHandlers(elem) {
      elem.querySelectorAll('.active .inferred').forEach((entity) => {
        entity.removeEventListener('click', this.itemClickHandler)
        entity.removeEventListener('mouseover', this.setHoverItem)
        entity.removeEventListener('mouseout', this.setHoverItem)
      })
    },

    setHoverItem(e) {
      this.hoverItem = e.type === 'mouseover' ? e.target.dataset.eid : null
    },
  
    itemClickHandler(e) {
      e.stopPropagation()
      this.selectedItem = e.target.dataset.eid 
      this.interactionHander(e)
    },

    getInteractionAttrs(elem) {
      const eventAttrs = []
      Array.from(elem.querySelectorAll(`span`)).forEach(span => {
        Array.from(span.attributes)
          .filter(attr => attr.name.indexOf('data-') === 0 && attr.name.split('-').length === 4)
          .map(attr => attr.name.split('-').slice(1,2)[0])
          .forEach(event => eventAttrs.push({elem: span, event}))
        })
      return eventAttrs
    },

    addInteractionHandlers(elem) {
      this.getInteractionAttrs(elem)
      .forEach(eventAttr => {
        eventAttr.elem.addEventListener(eventAttr.event, this.interactionHander)
        eventAttr.elem.classList.add('essay-interaction')
      })
    },

    removeInteractionHandlers(elem) {
      Array.from(elem.querySelectorAll('.essay-interaction')).forEach(span => {
        Array.from(span.attributes)
          .filter(attr => attr.name.indexOf('data-') === 0 && attr.name.split('-').length === 4)
          .map(attr => attr.name.split('-').slice(1,2)[0])
          .forEach(event => span.removeEventListener(event, this.interactionHander))
        span.classList.remove('essay-interaction')
      })
    },

    interactionHander(e) {
      e.stopPropagation()
      const eventActions = {};
      [...e.target.attributes, ...e.target.parentElement.attributes]
        .filter(attr => attr.name.indexOf(`data-`) === 0 && attr.name.split('-').length === 4)
        .map(attr => {
          const attrParts = attr.name.split('-').slice(1)
          const event = attrParts[0]
          const target = attrParts.slice(1,-1).join('-')
          const action = attrParts.slice(-1)[0]
          return { elem: e.target, event, target, action, value: attr.value } 
        })
        .filter(action => action.event === e.type)
        .forEach(action => {
          if (!eventActions[action.target]) eventActions[action.target] = []
          eventActions[action.target].push(action)
        })
      const actions = { ...this.actions }
      Object.keys(eventActions).forEach(target => actions[`${componentPrefix}${target}`] = eventActions[target])
      this.actions = actions
    }

  },
  watch: {
  
    scrollTop: {
      handler: function (scrollTop) { 
        if (this.$refs.viewer) this.viewerHeight = this.$refs.viewer.clientHeight
      },
      immediate: false
    },

    // Set app classes using essay config (ve-config) attributes, if present
    essayConfig (config) {
      this.layouts = []
      this.viewerIsOpen = false
      if (config) {
        if (config.layout) this.layouts = config.layout.split(',').map(layout => layout === 'vtl' ? 'vertical' : layout)
        if (config.title) document.title = this.siteConfig && this.siteConfig.title ? `${config.title} - ${this.siteConfig.title}` : config.title
        if (config.description) setMetaDescription(config.description)
      }
    },

    // Watcher that updates various data elements when the active paragraph changes
    active(current, prior) {
      let activeSegment = document.querySelector(`[data-id="${current}"]`)
      if (activeSegment) {
        if (this.$refs.tabsBar) activeSegment.appendChild(this.$refs.tabsBar)
        this.addItemEventHandlers(activeSegment)
        this.addInteractionHandlers(activeSegment)
      }
      let priorSegment = document.querySelector(`[data-id="${prior}"]`)
      if (priorSegment) {
        this.removeItemEventHandlers(priorSegment)
        this.removeInteractionHandlers(priorSegment)
      }
    },

    items: {
      handler: function (items) {
        let viewers = items.filter(item => this.availableViewers.indexOf(item.viewer) >= 0).map(item => item.viewer)
        let enabled = viewers.filter((viewer, index) => viewers.indexOf(viewer) === index)
        if (!arraysEqualIgnoreOrder(enabled, this.viewersEnabled)) this.viewersEnabled = enabled
      },
      immediate: true
    },

    availableViewers: {
      handler: function (availableViewers) {
        let viewers = this.items.filter(item => availableViewers.indexOf(item.viewer) >= 0).map(item => item.viewer)
        let enabled = viewers.filter((viewer, index) => viewers.indexOf(viewer) === index)
        if (!arraysEqualIgnoreOrder(enabled, this.viewersEnabled)) this.viewersEnabled = enabled
      },
      immediate: true
    },
    
    viewersEnabled: {
      handler: function (viewersEnabled) {
        this.selectedViewer = this.viewerIsOpen && viewersEnabled.length > 0 ? viewersEnabled[0] : null
        // console.log(`viewersEnabled: enabled=${viewersEnabled} selected=${this.selectedViewer}`)
      },
      immediate: true
    },

    isVerticalLayout: {
      handler: function () {
        this.selectedViewer = this.isVerticalLayout && this.viewersEnabled.length > 0 ? this.viewersEnabled[0] : this.selectedViewer
        if (this.isVerticalLayout) this.viewerIsOpen = true
      },
      immediate: true
    },

    hoverItem (eid) {
      document.querySelectorAll('.hover').forEach(el => el.classList.remove('hover'))
      document.querySelectorAll(`[data-eid="${eid}"]`).forEach(el => el.classList.add('hover'))        
    }
  }
})

Vue.config.productionTip = false
Vue.config.devtools = true

// Vue components mixin that handles linking to external JS and CSS resources
Vue.mixin({

  props: {
    componentName: String
  },

  data: () => ({
    dirCache: {}
  }),

  methods: {

    loadDependencies(dependencies, i, callback) {
      if (i === 0) {
        let componentData = {}
        componentData[this.componentName] = { label: this.viewerLabel, icon: this.viewerIcon }
        this.$emit('update-component-data', componentData)
      }
      if (dependencies && dependencies.length > 0) {
        this.load(dependencies[i], () => {
          if (i < dependencies.length-1) {
            this.loadDependencies(dependencies, i+1, callback) 
          } else {
            callback()
          }
        })
      } else {
        if (callback) callback()
      }
    },

    load(url, callback) {
      let e
      if (url.split('.').pop() === 'css') {
        e = document.createElement('link')
        e.href = url
        e.rel='stylesheet'
      } else {
        e = document.createElement('script')
        e.src = url
        e.type = url.indexOf('visual-essays.esm.js') > 0 ? 'module' : 'text/javascript'
      }
      e.addEventListener('load', callback)
      document.getElementsByTagName('head')[0].appendChild(e)
    },

    delimitedStringToObjArray(delimitedData, delimiter) {
      delimiter = delimiter || `\t`
      const objArray = []
      const lines = delimitedData.split('\n').filter(line => line.trim() !== '')
      if (lines.length > 1) {
        const keys = lines[0].split(delimiter).map(key => key.trim())
        lines.slice(1).forEach(line => {
          let obj = {}
          line.split(delimiter)
              .map(value => value.trim())
              .forEach((value, i) => {
                let rawKey = keys[i].split('.')
                let key = rawKey[0]
                let prop = rawKey.length === 2 ? rawKey[1] : 'id'
                if (!obj[key]) obj[key] = {}
                if (value || prop === 'id') obj[key][prop] = value
              })
          objArray.push(obj)
        })
        let assignedId = 0
        let labels = {}
        objArray.forEach(obj => {
          Object.values(obj).forEach(child => {
            if (child.id === '' && child.label) {
              if (!labels[child.label]) labels[child.label] = ++assignedId
              child.id = labels[child.label]
            }
          })
        })
      }
      return objArray
    },

    async dir(root, ghSource) {
      let cacheKey = ghSource ? `${ghSource.acct}/${ghSource.repo}/${ghSource.hash || ghSource.ref}${root}` : root
      if (!this.dirCache[cacheKey]) {
        let files = {}
        if (ghSource) {
          let url = `https://api.github.com/repos/${ghSource.acct}/${ghSource.repo}/git/trees/${ghSource.hash || ghSource.ref}`
          let pathElems = root.split('/').filter(pe => pe)
          let _dirList, found
          for (let i = 0; i < pathElems.length; i++) {
            _dirList = await this.ghDirList(url)
            found = _dirList ? _dirList.tree.find(item => item.path === pathElems[i]) : null
            url = found ? found.url : null
            if (!url) break
          }
          if (url) {
            _dirList = await this.ghDirList(url)
            files = Object.fromEntries(_dirList.tree.map(item => [item.path, `https://raw.githubusercontent.com/${ghSource.acct}/${ghSource.repo}/${ghSource.hash || ghSource.ref}${root}${item.path}`]))
          }
        }
        this.dirCache[cacheKey] = files
      }
      return this.dirCache[cacheKey]
    },

    async ghDirList(url) {
      let resp = await fetch(url, { headers: {Authorization: `Token ${ghToken}`}} )
      return resp.ok ? await resp.json() : null
    },

    async getFile(path, acct, repo, ref) {
      acct = acct || this.contentSource.acct
      repo = repo || this.contentSource.repo
      ref = ref || this.contentSource.ref
      // let ghToken = oauthAccessToken || ghUnscopedToken
      // console.log(`getFile: path=${path} acct=${acct} repo=${repo} ref=${ref} ghToken=${ghToken}`)
      if (repo) {
        let url = `https://api.github.com/repos/${acct}/${repo}/contents${path}?ref=${ref}`
        let resp = await fetch(url, ghToken ? {headers: {Authorization:`Token ${ghToken}`}} : {})
        if (resp.ok) {
          resp = await resp.json()
          return { sha: resp.sha, content: decodeURIComponent(escape(atob(resp.content))) }
        }
      } else {
        let url = `${this.contentSource.baseUrl}${this.contentSource.basePath}${path}`
        let resp = await fetch(url)
        if (resp.ok) resp = await resp.text()
        return {content: resp}
      }
      return null
    },

    async putFile(path, content, acct, repo, branch, message) {
      acct = acct || this.contentSource.acct
      repo = repo || this.contentSource.repo
      branch = branch || this.contentSource.ref
      message = message || 'API Commit'
      if (ENV === 'PROD' && acct) {
        // let ghToken = oauthAccessToken || ghUnscopedToken
        let existing = await this.getFile(path, acct, repo, branch)
        let payload = { message, branch, content: btoa(content) }
        if (existing) payload.sha = existing.sha
        let url = `https://api.github.com/repos/${acct}/${repo}/contents${path}?ref=${branch}`
        let resp = await fetch(url, { method: 'PUT', body: JSON.stringify(payload), headers: {Authorization: `Token ${ghToken}`} })
        resp = await resp.json()
      } else {
        let url = `${this.contentSource.baseUrl}${this.contentSource.basePath}${path}`
        let resp = await fetch(url, { method: 'PUT', body: content })
      }
    },

    convertLinks(root) {
      root.querySelectorAll('a').forEach(link => {
        if ((!link.href && link.dataset.target) || link.href.indexOf(window.location.host) > 0) {
          // If internal link
          let target = link.dataset.target
          if (!target) { 
            const parsedUrl = parseUrl(link.href)
            let pathElems = parsedUrl.pathname.split('/').filter(elem => elem !== '')
            if (contentSource.isGhpSite) {
              if (pathElems[0] === contentSource.repo) pathElems = pathElems.slice(1)
            } else {
              if (pathElems[0] === contentSource.acct && pathElems[1] === contentSource.repo) pathElems = pathElems.slice(2)
            }
            target = parsedUrl.hash === '' ? `/${pathElems.join('/')}${pathElems.length > 0 ? '/' : ''}` : parsedUrl.hash.split('?')[0]
          }
          link.removeAttribute('href')
          link.setAttribute('data-target', target)

          // Add click handler for internal links
          link.addEventListener('click', (e) => {
            let target = e.target
            while (!target.dataset.target && target.parentElement) { target = target.parentElement }
            let path = target.dataset.target
            if (path[0] === '#') {
              let anchorElem = document.getElementById(path.slice(1))
              if (anchorElem) anchorElem.scrollIntoView()
            } else {
              this.$emit('do-action', 'load-page', path)
            }
          })
        } else {
          // If external link, add external link icon to text and force opening in new tab
          link.innerHTML += '<sup><i class="fa fa-external-link-square-alt" style="margin-left:3px;margin-right:2px;font-size:0.7em;color:#219653;"></i></sup>'
          link.setAttribute('target', '_blank')
        }
      })
    }
  }
})


// Gets site config
async function getSiteConfig() {
  let config = await getGhFile('config.yaml')
  config = config ? YAML.parse(config) : {}
  if (config.banner) config.banner = convertURL(config.banner)

  // if (config.gcApiKey) gcApiKey = atob(config.gcApiKey)
  // if (config.gcAuthDomain) gcAuthDomain = atob(config.gcAuthDomain)
  // if (config.gaPropertyID) gaPropertyID = config.gaPropertyID
  // if (config.fontawesome) fontawesome = config.fontawesome
  return config
}

async function getContentSource() {
  let contentSource = {}
  let pathElems = window.location.pathname.split('/').filter(elem => elem !== '')
  let ghRepoInfo = await githubRepoInfo(pathElems[0], pathElems[1])
  contentSource = {
    ...ghRepoInfo, 
    ...{
      baseUrl: window.location.origin, 
      basePath: `/${ghRepoInfo.acct}/${ghRepoInfo.repo}`, 
      assetsBaseUrl: `https://raw.githubusercontent.com/${ghRepoInfo.acct}/${ghRepoInfo.repo}/${ghRepoInfo.ref}`
    }
  }
  return contentSource
}

async function githubRepoInfo(acct, repo) {
  let ghInfo = {}
  let resp = await fetch(`https://api.github.com/repos/${acct}/${repo}`, {headers: {Authorization: `Token ${ghToken}`}} )
  if (resp.ok) {
    resp = await resp.json()
    ghInfo = {acct, repo, branch: resp.default_branch, ref: qargs.ref || resp.default_branch}
  }
  return ghInfo
}

  
async function isDir(root, ghSource) {
  let dirList = await dir(root, ghSource)
  return Object.keys(dirList).length > 0
}

async function dir(root, ghSource) {
  let cacheKey = ghSource ? `${ghSource.acct}/${ghSource.repo}/${ghSource.hash || ghSource.ref}${root}` : root
  if (!dirCache[cacheKey]) {
    let files = {}
    if (ghSource) {
      let url = `https://api.github.com/repos/${ghSource.acct}/${ghSource.repo}/git/trees/${ghSource.hash || ghSource.ref}`
      let pathElems = root.split('/').filter(pe => pe)
      let _dirList, found
      for (let i = 0; i < pathElems.length; i++) {
        _dirList = await ghDirList(url)
        found = _dirList ? _dirList.tree.find(item => item.path === pathElems[i]) : null
        url = found ? found.url : null
        if (!url) break
      }
      if (url) {
        _dirList = await ghDirList(url)
        files = Object.fromEntries(_dirList.tree.map(item => [item.path, `https://raw.githubusercontent.com/${ghSource.acct}/${ghSource.repo}/${ghSource.hash || ghSource.ref}${root}/${item.path}`]))
      }
    }
    dirCache[cacheKey] = files
  }
  return dirCache[cacheKey]
}

async function ghDirList(url) {
  let resp = await fetch(url, { headers: {Authorization: `Token ${ghToken}`}} )
  return resp.ok ? await resp.json() : null
}

// Gets a list of available components
async function getComponentsList() {
  return [
    ...Object.values(await dir('/custom/components', contentSource)),
    ...Object.values(await dir('/components', contentSource)),
    ...Object.values(await dir('/components', {acct: 'jstor-labs', repo: 'juncture', hash: 'v2'}))
  ]
}

async function getGhFile(path) {
  let url = `https://api.github.com/repos/${contentSource.acct}/${contentSource.repo}/contents${path}?ref=${contentSource.ref}`
  let resp = await fetch(url, ghToken ? {headers: {Authorization:`Token ${ghToken}`}} : {})
  if (resp.ok) {
    resp = await resp.json()
    return decodeURIComponent(escape(atob(resp.content)))
  }
}

function parseQueryString(queryString) {
  queryString = queryString || window.location.search
  const dictionary = {}
  try {
    if (queryString.indexOf('?') === 0) queryString = queryString.substr(1)
    const parts = queryString.split('&')
    for (let i = 0; i < parts.length; i++) {
      const kvp = parts[i].split('=')
      if (kvp[0] !== '') {
        if (kvp.length === 2) {
          dictionary[kvp[0]] = decodeURIComponent(kvp[1]).replace(/\+/g, ' ')
        } else {
          dictionary[kvp[0]] = 'true'
        }
      }
    }
  } catch (err) { console.log(err) }
  return dictionary
}

function getDomPath(el) {
  var stack = []
  while ( el.parentNode != null ) {
    let sibCount = 0
    let sibIndex = 0
    for ( var i = 0; i < el.parentNode.childNodes.length; i++ ) {
      let sib = el.parentNode.childNodes[i];
      if ( sib.nodeName == el.nodeName ) {
        if ( sib === el ) {
          sibIndex = sibCount;
        }
        sibCount++
      }
    }
    if ( el.hasAttribute('id') && el.id != '' ) {
      stack.unshift(el.nodeName.toLowerCase() + `#${el.id}`)
    } else if ( sibCount > 1 ) {
      stack.unshift(el.nodeName.toLowerCase() + (sibIndex > 0 ? `[${sibIndex}]` : ''))
    } else {
      stack.unshift(el.nodeName.toLowerCase())
    }
    el = el.parentNode
  }
  return stack
}
function setMetaDescription(description) {
  let existing = Array.from(document.querySelectorAll('meta[name=description]')).find(item => item)
  if (existing) existing.parentElement.removeChild(existing)
  let el = document.createElement('meta')
  el.name = 'description'
  el.content = description
  document.querySelector('head').appendChild(el)
}
function camelToKebab(input) { return input.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase()}
function isNumeric(arg) { return !isNaN(arg) }
function isEntityID(arg) { return typeof arg === 'string' && arg.split(':').slice(-1).find(val => val.length > 1 && val[0] === 'Q' && isNumeric(val.slice(1))) !== undefined }
function attrsToObject(el) { return Object.fromEntries(Array.from(el.attributes).map(attr => [attr.nodeName, attr.value === '' || attr.value === 'true' ? true : attr.value === 'false' ? false : attr.value] )) }
function arraysEqualIgnoreOrder(a, b) {
  if (a.length !== b.length) return false
  const uniqueValues = new Set([...a, ...b])
  for (const v of uniqueValues) {
    const aCount = a.filter(e => e === v).length
    const bCount = b.filter(e => e === v).length
    if (aCount !== bCount) return false
  }
  return true
}
function parseUrl(href) {
  const match = href.match(/^(https?):\/\/(([^:/?#]*)(?::([0-9]+))?)(\/?[^?#]*)(\?[^#]*|)(#.*|)$/)
  return (match && {protocol: match[1], host: match[2], hostname: match[3], origin: `${match[1]}://${match[2]}`,
          port: match[4], pathname: match[5] || '/', search: match[6], hash: match[7]}
  )
}

function convertURL(current, base) {
  base = base || '/'
  let _current = current.replace(/\s/g, '%20')
  let pathElems = []
  if (_current.indexOf('http') === 0) {
    if (_current.indexOf(window.location.origin) === 0) {
      let dirElems = base.split('/').filter(elem => elem).slice(0,-1)
      let mdDir = dirElems.length > 0 ? `/${dirElems.join('/')}/` : '/'
      _current = _current.replace(new RegExp(base.replace(/\//g, '\\/')), `${mdDir}`)
      pathElems = _current.split('/').slice(3)
    }
    else return _current
  } else if (_current.indexOf('/') === 0) {
    pathElems = _current.split('/').filter(elem => elem)
  } else {
    pathElems = (base || window.location.pathname).split('/').filter(elem => elem)
    pathElems = [...pathElems, ..._current.split('/').filter(elem => elem)]
  }
  if (isJuncture && pathElems.length >= 2) {
    if ((contentSource.repo !== 'juncture' || contentSource.acct !== 'jstor-labs') && pathElems[0] === contentSource.acct && pathElems[1] === contentSource.repo) pathElems = pathElems.slice(2)
  } else if (pathElems[0] === contentSource.repo) {
    pathElems = pathElems.slice(1)
  }
  let converted = `${contentSource.assetsBaseUrl || contentSource.baseUrl}/${pathElems.join('/')}`
  // console.log(`isJuncture=${isJuncture} convertURL: current=${current} converted=${converted} path=${path} pathElems=${pathElems}`)
  return converted
}