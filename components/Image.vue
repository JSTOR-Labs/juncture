<template>
  <div class="image-viewer" :style="osdContainerStyle">
    
      <div class="osd" id="osd"></div>
      <div id="osd-toolbar" class="controls auto-hide">
        <span id="go-home"><i class="fas fa-home"></i></span>
        <span id="zoom-in"><i class="fas fa-search-plus"></i></span>
        <span id="zoom-out"><i class="fas fa-search-minus"></i></span>
        <span class="info-box"><i class="fas fa-info-circle"></i></span>

        <span v-if="hasAnnotations" @click="showAnnotations = !showAnnotations" title="Show Annotations">
          <i class="far fa-comment-dots"></i>
        </span>
        <span v-if="hasAnnotations" @click="showAnnotationsNavigator = !showAnnotationsNavigator" title="Play Annotations" style="height:40px;">
          <svg width="19" height="20" viewBox="0 0 20 21" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M13.3333 8L7.77778 12.4444V3.55556L13.3333 8ZM2.22222 0H17.7778C19 0 20 1 20 2.22222V13.7778C20 15 19 16 17.7778 16H11.885L14.2682 18.8598C14.6218 19.2841 14.5645 19.9147 14.1402 20.2682C13.7159 20.6218 13.0853 20.5645 12.7318 20.1402L9.75 16.562L6.76822 20.1402C6.41466 20.5645 5.78409 20.6218 5.35982 20.2682C4.93554 19.9147 4.87821 19.2841 5.23178 18.8598L7.61496 16H2.22222C1 16 0 15 0 13.7778V2.22222C0 1 1 0 2.22222 0ZM2.22222 13.7778H17.7778V2.22222H2.22222V13.7778Z"/>
          </svg>
        </span>
        <span v-if="isAuthenticated" @click="toggleAnnotatorEnabled" title="Edit Annotations" style="height:40px;" id="annotatorIcon">
          <svg width="21" height="18" viewBox="0 0 22 19" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M20.6453 5.5585L17.0283 4.25559C16.8759 4.2007 16.7039 4.27914 16.6455 4.43017L13.2845 13.1108L14.1453 15.7556C14.2596 16.1093 14.6807 16.2609 15.0074 16.0661L17.4548 14.613L20.8158 5.93242C20.8743 5.78138 20.7977 5.61339 20.6453 5.5585ZM19.2831 0.880764L21.2399 1.58566C21.8495 1.80522 22.1546 2.47448 21.9219 3.08134L21.3772 4.48836C21.3187 4.6394 21.1467 4.71783 20.9943 4.66294L17.3774 3.36003C17.225 3.30514 17.1484 3.13715 17.2069 2.98611L17.7516 1.57909C17.9883 0.973681 18.6736 0.661205 19.2831 0.880764ZM10.6142 12.8025L14.7886 2.84821C13.8401 2.62062 12.8308 2.49796 11.784 2.49796C6.24285 2.49796 1.75304 5.93501 1.75304 10.1785C1.75304 11.825 2.43302 13.3419 3.58562 14.5948C2.98452 15.9433 0.742171 17.2336 0.420251 17.4188C0.39608 17.4327 0.382736 17.4404 0.381725 17.4414C0.275629 17.5518 0.246694 17.715 0.309387 17.8591C0.37208 18.0031 0.507112 18.0895 0.661434 18.0895C2.42649 18.0895 5.36514 17.2686 6.41646 16.659C7.96933 17.4126 9.80673 17.8591 11.784 17.8591C12.0419 17.8591 12.2976 17.8516 12.5506 17.837L10.6142 12.8025Z"/>
        </svg>
        </span>
      </div>
      <div class="viewport-coords auto-hide" v-text="imageViewportCoords" @click="copyTextToClipboard" title="Copy viewable image coords"></div>

      <div class="annotations" v-if="hasAnnotations && showAnnotationsNavigator">
        <div class="anno-controls">
          <div class="anno-nav">
            <span @click="viewPreviousAnnotation" title="Previous">
              <i class="fas fa-arrow-left"></i>
            </span>
            <span class="anno-controls-text">{{annoCursor+1}} of {{numAnnotations}} annotations</span>
            <span @click="viewNextAnnotation" title="Next">
              <i class="fas fa-arrow-right"></i>
            </span>
          </div>
          <div class="anno-close" @click="showAnnotationsNavigator = false" title="Exit Annotations Navigator"><i class="far fa-times-circle"></i></div>
        </div>
        <div class="annos" v-html="annoText" @click="copyAnnoIdToClipboard"></div>
      </div>
  
      <input v-if="viewerItems && viewerItems.length > 1 && (mode === 'layers' || mode === 'curtain')"
            class="slider" 
            v-model="sliderPct" type="range" min="0" max="100" value="0"
      >
      
      <div class="citation">
        <span v-if='title || itemLabel || description' v-html="title || itemLabel || description" class="image-label"></span><br>
        <span v-if="attribution" v-html="attribution" class="attribution"></span>
        <span v-if="licenseUrl" class="licenses">
          <a :href="licenseUrl" target="_blank">
            <i v-for="(icon, idx) in licenseIcons" :key="idx" :class="icon"></i>
          </a>
        </span>
      </div>
    </div>
</template>

<script>
/* global _, OpenSeadragon, sjcl */

const iiifService = window.config?.defaults?.iiifServer ? `https://${window.config?.defaults?.iiifServer}` : 'https://iiif.juncture-digital.org'

const viewerLabel = 'Image Viewer'
const viewerIcon = 'far fa-file-image'

const prefixUrl = 'https://openseadragon.github.io/openseadragon/images/'

const dependencies = [
  'https://cdn.jsdelivr.net/npm/openseadragon@2.4/build/openseadragon/openseadragon.min.js',
  'https://cdn.jsdelivr.net/npm/@recogito/annotorious-openseadragon@2.5.3/dist/annotorious.min.css',
  'https://cdn.jsdelivr.net/npm/@recogito/annotorious-openseadragon@2.5.3/dist/openseadragon-annotorious.min.js',
  'https://cdn.jsdelivr.net/npm/sjcl@1.0.8/sjcl.min.js'
]

const ccLicenseIcons = {
  PD: 'fab fa-creative-commons-pd',
  CC: 'fab fa-creative-commons',
  CC0: 'fab fa-creative-commons-zero',
  BY: 'fab fa-creative-commons-by',
  SA: 'fab fa-creative-commons-sa',
  NC: 'fab fa-creative-commons-nc',
  ND: 'fab fa-creative-commons-nd'
}

module.exports = {
  name: 've1-image',
  props: {
    items: Array,
    viewerIsActive: Boolean,
    actions: { type: Object, default: () => ({}) },
    contentSource:  { type: Object, default: () => ({}) },
    mdDir: String,

    actionSources: { type: Array, default: () => ([]) },
    siteInfo: { type: Object, default: () => ({}) },

    path: String,

    width: Number,
    height: Number,
    selected: String,
    jwt: String,
    serviceBase: String
  },
  data: () => ({
    viewerIcon,
    viewerLabel,
    dependencies,
    prefixUrl,
    manifests: undefined,
    page: 0,
    goToRegionCoords: null,
    currentItem: undefined,
    viewer: undefined,
    imageSize: {x:0,y:0},
    annotator: undefined,
    annotations: [],
    annoCursor: 0,
    overlay: undefined,
    annosEditor: undefined,
    sliderPct: 0,
    tileSources: [],
    showAnnotations: false,
    showAnnotationsNavigator: false,
    licenseUrl: null,
    licenseIcons: [],
    imageViewportCoords: null,
    osdElem: null,
    tippy: null,
    imageInfo: null,
    showTippy: false,
    annotatorEnabled: false,
  }),
  computed: {
    osdContainerStyle() {
      return {
        background: this.currentItem && this.currentItem.background ? this.currentItem.background : 'black',
        textAlign: 'center',
        height: this.viewerIsActive ? '100%' : '0',
        display: this.viewerIsActive ? 'grid' : 'none',
        width: `${this.width}px`,
        maxHeight: this.showAnnotations ? `${this.width}px` : '',
        position: 'relative'
      }
    },
    viewerItems() { return this.items
      .filter(item => item.viewer === this.$options.name)
      .map(item => {
        if (item.manifest && item.manifest?.indexOf('http') !== 0) {
          item.manifest = `${iiifService}/${item.manifest}/manifest.json`
        }
        return item
      }) 
    },
    manifest() { return this.currentItem ? `<a href="${this.currentItem.manifest}"><img src="https://upload.wikimedia.org/wikipedia/commons/e/e8/International_Image_Interoperability_Framework_logo.png" height="30" width="30"></a>` : null},
    mode() { return this.viewerItems.length > 0 ? this.viewerItems[0].mode || 'gallery' : 'gallery'},
    fit() { return this.currentItem && this.currentItem.fit
      ? this.currentItem.fit
      : this.mode === 'gallery'
        ? 'cover'
        : 'contain'
    },
    currentItemSource() {
      return this.currentItem && this.findItem({type:'Annotation', motivation:'painting'}, this.currentItem, this.currentItem.seq || 1).body.id
    },
    currentItemSourceHash() {
      let hashFromMetadata = this.currentItem?.metadata.find(md => md.label?.en?.[0] === 'hash')?.value.en?.[0]
      return hashFromMetadata
        ? hashFromMetadata
        : this.currentItemSource
          ? this.sha256(this.currentItemSource).slice(0,8)
          : ''
    },
    annosUrl() { return `${this.contentSource.assetsBaseUrl || this.contentSource.baseUrl}/${this.mdDir}${this.currentItemSourceHash}.json` },
    target() {
      if (this.currentItem.target) {
        return this.currentItem.target
      } else {
        let path = `${window.location.pathname.split('/').filter(elem => elem !== '').join('/')}`
        const imageSourceHash = this.currentItem ? this.sha256(this.currentItem['@id']).slice(0,8) : ''
        return `${this.contentSource.acct}/${this.contentSource.repo}/${this.contentSource.ref}${path ? '/'+path : ''}/${imageSourceHash}`
      }
    },
    numAnnotations() { return this.annotations.length },
    hasAnnotations() { return this.numAnnotations > 0 },
    hasNextAnnotation() { return this.annoCursor < this.numAnnotations - 1 },
    hasPreviousAnnotation() { return this.annoCursor > 0 },
    annoText() { return this.hasAnnotations ? this.annotations[this.annoCursor].body[0].value : '' },
    metadata() {
      return this.currentItem && this.currentItem.metadata 
        ? Object.fromEntries(this.currentItem.metadata.map(md => [md.label, md.value])) 
        : {}
    },
    itemLabel() {
      return this.currentItem && this.metadata && this.metadata.title_formatted
        ? this.metadata.title_formatted
        : this.currentItem && this.currentItem.label
          ? this.currentItem.label['@value'] || (this.currentItem.label.en ? this.currentItem.label.en[0] : this.currentItem.label)
          : null
    },
    title() { return this.currentItem?.title },
    description() { return this.currentItem ? this.currentItem.description || this.metadata.description : null },
    attribution() { return this.currentItem ? this.currentItem.attribution || this.metadata.attribution : null },
    date() { return this.currentItem ? this.currentItem.date || this.metadata.date : null },
    license() { return this.currentItem ? this.currentItem.license || this.metadata.license : null },
    annosEndpoint() { return `${this.serviceBase}/annotations/`},
    annosTool() { return `${this.serviceBase}/annotator`},
    ghToken() { return localStorage.getItem('gh-auth-token') },
    isAuthenticated() { return this.ghToken },
    source() {
      if (this.metadata.info && this.metadata.info.indexOf('http') === 0) {
        return `Source: <a href="${this.metadata.info}" target="_blank">${this.metadata.info}</a>`
      } else {
        return `Source: ${this.metadata.info || ''}`
      }
    }    
  },
  mounted() {
    this.osdElem = document.getElementById('osd')
    const osdElem = document.getElementById('osd')
    if (osdElem) { osdElem.style.background = this.osdContainerStyle.background }
    this.loadDependencies(dependencies, 0, this.init)
  },
  methods: {
    init() {
      if (this.viewerIsActive) {
        this.initViewer()
        this.loadManifests(this.viewerItems).then(manifests => this.manifests = manifests)
      }
    },
    sha256(s) {
      return sjcl.codec.hex.fromBits(sjcl.hash.sha256.hash(s))
    },
    initViewer() {
      if (this.viewer) {
        this.viewer = this.viewer.destroy()
      }
      this.$nextTick(() => {
        let options = {
          id: 'osd',
          prefixUrl: 'https://openseadragon.github.io/openseadragon/images/',
          zoomInButton:   'zoom-in',
          zoomOutButton:  'zoom-out',
          homeButton:     'go-home',
          visibilityRatio: 1.0,
          constrainDuringPan: true,
          minZoomImageRatio: 0.6,
          maxZoomPixelRatio: 10,
          homeFillsViewer: this.fit === 'cover',
          viewportMargins: {left:0, top:0, bottom:0, right:0},
          sequenceMode: true,
          showReferenceStrip: true,
          showNavigationControl: true,
          showHomeControl: true,
          showZoomControl: true,
          showFullPageControl: false,
          showSequenceControl: false,
          showNavigator: false
        }
        if (this.mode === 'layers' || this.mode === 'curtain') {
          options = { ...options, ...{
            sequenceMode: false,
            showReferenceStrip: false
          }}
        } else if (this.mode === 'compare') {
          options = { ...options, ...{
            sequenceMode: false,
            showReferenceStrip: false,
            collectionMode: true,
            collectionRows: 1
          }}  
        }
        this.viewer = OpenSeadragon(options)
        this.initAnnotator()

        this.viewer.addHandler('home', (e) => {
          this.positionImage(e.immediately, 'home')
        })
        this.viewer.addHandler('page', this.newPage)
        this.viewer.addHandler('viewport-change', this.viewportChange)
        this.viewer.world.addHandler('add-item', (e) => {
          const numItems = this.viewer.world.getItemCount()
          if (this.currentItem && this.currentItem.rotate) {
            e.item.setRotation(parseInt(this.currentItem.rotate), true)
          }
          if (this.mode === 'curtain' && numItems > 1) {
            this.viewer.world.getItemAt(numItems-1).setClip(new OpenSeadragon.Rect(0, 0, 0, 0))
          }
          this.imageSize = e.item.getContentSize() || {x:0 , y:0}

        })
      })
    },
    loadTileSources() {
      if (this.tileSources.length > 0) this.viewer.open(this.tileSources)
    },
    toggleShowAnnotations() {
      this.showAnnotations = !this.showAnnotations
    },
    toggleAnnotationsNavigators() {
      this.showAnnotationsNavigator = !this.showAnnotationsNavigator
    },
      
    // find an item in a IIIF manifest
    findItem(toMatch, current, seq = 1) {
      const found = this._findItems(toMatch, current)
      return found.length >= seq ? found[seq-1] : null
    },

    // recursive helper for finding items in a IIIF manifest
    _findItems(toMatch, current, found = []) {
      found = found || []
      if (current.items) {
        for (let i = 0; i < current.items.length; i++ ) {
          let item = current.items[i]
          let isMatch = !Object.entries(toMatch).find(([attr, val]) => item[attr] && item[attr] !== val)
          if (isMatch) found.push(item)
          else this._findItems(toMatch, item, found)
        }
      }
      return found
    },
    
    async loadManifests(items) {
      let requests = items.map(item => {
        if (item.manifest) return fetch(item.manifest)
        else if (item.url) {
          let data = {};
          ['url', 'label', 'description', 'attribution', 'license'].forEach(field => {
            if (item[field]) data[field] = item[field]
          })
          return fetch(`${iiifService}/manifest/`, {
            method: 'POST',
            headers: {'Content-type': 'application/json'},
            body: JSON.stringify(data)
          })
        } 
      })
      let responses = await Promise.all(requests)
      let manifests = await Promise.all(responses.map(resp => resp.json()))
      requests = manifests
        .filter(manifest => !Array.isArray(manifest['@context']) && parseFloat(manifest['@context'].split('/').slice(-2,-1).pop()) < 3)
        .map(manifest => fetch(`${iiifService}/prezi2to3/`, {
          method: 'POST', 
          body: JSON.stringify(manifest)
        }))
      if (requests.length > 0) {
        responses = await Promise.all(requests)
        let convertedManifests = await Promise.all(responses.map(resp => resp.json()))
        for (let i = 0; i < manifests.length; i++) {
          let mid =  manifests[i].id ||manifests[i]['@id']
          let found = convertedManifests.find(manifest => (manifest.id || manifest['@id']) === mid)
          if (found) manifests[i] = found
        }
      }
      return manifests
    },

    // convert IIIF v2 manifest to v3; all operations in this component are based on v3
    async prezi2to3(manifest) {
      let resp = await fetch(`${iiifService}/prezi2to3/`, {
        method: 'POST', 
        body: JSON.stringify(manifest)
      })
      if (resp.ok) return (await resp).json()
    },

    positionImage (immediately) {
      immediately = immediately || false
      if (this.currentItem) {
        this.$nextTick(() => {
          if (this.currentItem.region) {
            this.viewer.viewport.fitBounds(this.parseRegionString(this.currentItem.region), immediately)
          } else {
            const scaleX = this.osdElem.clientHeight/this.imageSize.y
            const scaleY = this.osdElem.clientWidth/this.imageSize.x
            const fit = this.fit === 'cover'
              ? scaleY/scaleX > 1 ? 'horizontal' : 'vertical'
              : scaleY/scaleX > 1 ? 'vertical' : 'horizontal'
            if (fit === 'horizontal') {
              this.viewer.viewport.fitHorizontally(immediately)
            } else {
              this.viewer.viewport.fitVertically(immediately)
            }
          }
        })
      }
    },
    goHome(immediately) {
      immediately = immediately || false
      if (this.viewer) this.viewer.viewport.goHome(immediately)
    },
    viewportChange: _.debounce(function () {
      const viewportBounds = this.viewer.viewport.getBounds()
      const tiledImage = this.viewer.world.getItemAt(0)
      if (tiledImage) {
        const imageBounds = tiledImage.viewportToImageRectangle(viewportBounds)
        this.imageViewportCoords = `${Math.ceil(imageBounds.x)},${Math.ceil(imageBounds.y)},${Math.ceil(imageBounds.width)},${Math.ceil(imageBounds.height)}`
      }
      if (this.zoomtoRegion) {
        this.gotoRegion(this.zoomtoRegion)
        this.zoomtoRegion = null
      }
    }, 100),
    newPage(e) {
      this.page = e.page
    },
    initAnnotator() {
      if (!this.annotator) {
        this.annotator = OpenSeadragon.Annotorious(this.viewer, { readOnly: !this.isAuthenticated })
        this.annotator.off()
        this.annotator.on('selectAnnotation', this.annotationSelected)
        this.annotator.on('createAnnotation', this.saveAnnotations)
        this.annotator.on('updateAnnotation', this.saveAnnotations)
        this.annotator.on('deleteAnnotation', this.saveAnnotations)
      }
    },
    async loadAnnotations() {
      let annosFile = `${this.currentItemSourceHash}.json`
      let path = `${this.mdDir}/${annosFile}`
      this.getFile(path, this.contentSource.acct, this.contentSource.repo, this.contentSource.ref).then(annos => {
        if (annos && annos.content) {
          this.annotations = annos.content.items
            ? annos.content.items
            : annos.content
          if (!Array.isArray(this.annotations) && this.annotations.items) this.annotations = this.annotations.items

          this.annotations.forEach(anno => this.annotator.addAnnotation(anno))
        } else {
          this.annotations = []
        }
        this.annoCursor = 0
        if (this.annotations.length > 0) this.showAnnotationsNavigator = true
      })
    },
    async getFile(path, acct, repo, branch) {
      acct = acct || window.config?.github?.owner_name, 
      repo = repo || window.config?.github?.repository_name
      branch = branch || window.config?.github?.source?.branch
      // console.log(`getFile: acct=${acct} repo=${repo} branch=${branch} path='${path}`)
      let url = `https://api.github.com/repos/${acct}/${repo}/contents${path}?ref=${branch}`
      let resp = await fetch(url)
      if (resp.ok) {
        resp = await resp.json()
        return { sha: resp.sha, content: JSON.parse(decodeURIComponent(escape(atob(resp.content)))) }
      } else {
        return null
      }
    },
    async putFile(path, content, acct, repo, branch, message) {
      acct = acct || this.contentSource.acct || window.config?.github?.owner_name
      repo = repo || this.contentSource.repo || window.config?.github?.repository_name
      branch = branch || this.contentSource.ref || window.config?.github?.source?.branch
      message = message || 'API Commit'
      if (acct) {
        let existing = await this.getFile(path, acct, repo, branch)
        let payload = { message, branch, content: btoa(content) }
        if (existing) payload.sha = existing.sha
        // console.log(`putFile: acct=${acct} repo=${repo} branch=${branch} path='${path} sha=${existing ? existing.sha : ''}`)
        let url = `https://api.github.com/repos/${acct}/${repo}/contents${path}?ref=${branch}`
        let resp = await fetch(url, { method: 'PUT', body: JSON.stringify(payload), headers: {Authorization: `Token ${this.ghToken}`} })
        resp = await resp.json()
      }
    },
    saveAnnotations() {
      this.annotations = this.annotator.getAnnotations()
      this.putFile(`${this.mdDir}/${this.currentItemSourceHash}.json`, JSON.stringify(this.annotations, null, 2))
    },
    annotationSelected(anno) {
    },
    toggleAnnotatorEnabled() {
     this.annotatorEnabled = !this.annotatorEnabled
     if (this.annotatorEnabled) {
      document.getElementById("annotatorIcon").style.backgroundColor = "#f5e753";
     } else {
      document.getElementById("annotatorIcon").style.backgroundColor = "transparent";
     }
      
    },
    setAnnotatorEnabled(enabled) {
      const osdElem = document.getElementById('osd')
      this.annotator.readOnly = !this.isAuthenticated
      if (osdElem) {
        osdElem.style.maxHeight = enabled ? `${this.width}px` : ''
        Array.from (document.querySelectorAll('.a9s-annotationlayer')).forEach(elem => elem.style.display = enabled ? 'unset' : 'none')
        setTimeout(() => this.goHome(true), 10)
      }
    },
    openAnnotationsEditor() {
      const url = `${this.annosTool}?manifest=${encodeURIComponent(this.currentItem['manifest'])}&target=${encodeURIComponent(this.target)}&jwt=${this.jwt}`
      if (this.annosEditor) { this.annosEditor.close() }
      this.annosEditor = window.open(url, '_blank', `toolbar=yes,location=yes,left=0,top=0,width=1400,height=1200,scrollbars=yes,status=yes`)
    },
    viewNextAnnotation() {
      this.gotoAnnotationSeq(this.hasNextAnnotation ? this.annoCursor + 1 : 0)
    },
    viewPreviousAnnotation() {
      this.gotoAnnotationSeq(this.hasPreviousAnnotation ? this.annoCursor - 1 : this.numAnnotations - 1)
    },
    gotoAnnotationSeq(idx) {
      idx = idx !== undefined ? idx : this.annoCursor
      if (idx < this.annotations.length) {
        this.annoCursor = idx
        this.gotoAnnotation(this.annotations[idx])
      }
    },
    gotoAnnotation(anno) {
      this.showAnnotationsNavigator = true
      this.gotoRegion(anno.target.selector.value.split('=')[1])
    },
    gotoPage(page, region) {
      this.viewer.goToPage(page);
      this.gotoRegion(region)
    },
    gotoRegion(region) {
      this.viewer.viewport.zoomSpring.animationTime = 2
      let bounds = this.parseRegionString(region)
      this.viewer.viewport.fitBounds(bounds)
      this.viewer.viewport.zoomSpring.animationTime = 1.2
    },
    copyTextToClipboard(e) {
      if (navigator.clipboard) navigator.clipboard.writeText(e.target.textContent)
    },
    copyAnnoIdToClipboard() {
      if (navigator.clipboard) navigator.clipboard.writeText(this.annotations[this.annoCursor].id.split('/').pop())
    },
    findAnnotation(annoId) {
      return this.annotations.find(anno => annoId === anno.id.split('/').pop())
    },
    parseRegionString(region) {
      const s1 = region.split(':')
      let ints = s1[s1.length-1].split(',').map(v => parseInt(v))
      if (ints.length === 4) {
        if (s1.length === 1 || (s1.length === 2 && (s1[0] === 'px' || s1[0] === 'pixel'))) {
          return this.viewer.viewport.imageToViewportRectangle(new OpenSeadragon.Rect(...ints))
        } else if (s1.length === 2 && (s1[0] === 'pct' || s1[0] === 'percent')) {
          const size = this.viewer.world.getItemAt(0).getContentSize()
          if (size.x > 0 && size.y > 0) {
            return this.viewer.viewport.imageToViewportRectangle(
              Math.round(size.x * ints[0]/100),
              Math.round(size.y * ints[1]/100),
              Math.round(size.x * ints[2]/100), 
              Math.round(size.y * ints[3]/100)
            )
          }
        }
      }
    },
    handleEssayAction({elem, event, action, value}) { // eslint-disable-line no-unused-vars
      let region
      let anno = this.findAnnotation(value)
      if (!anno) region = value
      switch(event) {
          case 'click':
              switch(action) {
                case 'zoomto':
                  if (anno) {
                    this.gotoAnnotation(anno)
                  } else {
                    if (region == 'next'){
                      //go to next page
                      if (this.page+1 <= this.manifests.length){
                        this.viewer.goToPage(this.page+1)
                      }

                    }
                    else if (region == 'previous'){
                      //go to previous page
                      if (this.page-1 > -1){
                        this.viewer.goToPage(this.page-1)
                      }
                    }
                    else if (!region.includes(',')){
                      let zoomtoPage = this.manifests.findIndex(obj => obj.ref === region)
                      if (zoomtoPage >= 0) {
                        this.page = zoomtoPage;
                        this.viewer.goToPage(zoomtoPage)
                      }
                    }
                    else if (region.includes('|')) {
                      let [ zoomtoRef, zoomtoRegion ] = region.split('|')
                      let zoomtoPage = this.manifests.findIndex(obj => obj.ref === zoomtoRef)
                      if (zoomtoPage >= 0) {
                        this.page = zoomtoPage;
                        this.zoomtoRegion = zoomtoRegion
                        this.viewer.goToPage(zoomtoPage)
                      }
                    } else {
                      this.gotoRegion(region)
                    }
                  }
                  break
                
              }                        
              break
          case 'mouseover':
              switch(action) {
                case 'zoomto':
                  if (anno) {
                    this.gotoAnnotation(anno)
                  } else {
                    this.gotoRegion(region)
                  }
                  break
              }                        
              break
      }
    },
    recursivelyOrderKeys(unordered) {
      // If it's an array - recursively order any
      // dictionary items within the array
      if (Array.isArray(unordered)) {
        unordered.forEach((item, index) => {
          unordered[index] = this.recursivelyOrderKeys(item)
        })
        return unordered
      }
      // If it's an object - let's order the keys
      if (typeof unordered === 'object') {
        var ordered = {}
        Object.keys(unordered).sort().forEach(key => {
          ordered[key] = this.recursivelyOrderKeys(unordered[key])
        })
        return ordered
      }
      return unordered
    },
    stringifyKeysInOrder(data) {
      var sortedData = this.recursivelyOrderKeys(data)
      return JSON.stringify(sortedData, null)
    },
    evalLicense() {
      const versionRegex = RegExp(`^[0-9.]+$`)
      let licenseCode, licenseUrl, licenseIcons
      if (this.license) {
        if (this.license.indexOf('http') === 0) {
          licenseUrl = this.license
          if (this.license.indexOf('creativecommons.org') > 0) {
            const pathElems = this.license.split('/').filter(p => p !== '').slice(2)
            const ccVersion = pathElems.find(pe => versionRegex.test(pe))
            if (pathElems[0] === 'publicdomain') {
              licenseCode = pathElems[1] === 'zero' ? `CC0 ${ccVersion}` : 'PD'
            } else if (pathElems[0] === 'licenses') {
              licenseCode = `CC ${pathElems[1].toUpperCase()} ${ccVersion}`
            }
          }
        } else {
          licenseCode = this.license.toUpperCase()
        }
      }
      if (licenseCode) {
        if (licenseCode.toUpperCase() === 'PD' || licenseCode.toUpperCase() === 'public domain') {
          
          licenseUrl = licenseUrl || 'https://creativecommons.org/publicdomain/mark/1.0'
          licenseIcons = [ccLicenseIcons.PD]
        } else if (licenseCode.indexOf('CC0') === 0) {
          licenseUrl = licenseUrl || 'https://creativecommons.org/publicdomain/zero/1.0'
          licenseIcons = [ccLicenseIcons.CC, ccLicenseIcons.CC0]
        } else if (licenseCode == 'NO KNOWN COPYRIGHT RESTRICTIONS') {
          //do nothing
          licenseIcons = [];
        } else {
          let icons = []
          const ccVersion = licenseCode.split(' ').pop()
          const ccTerms = licenseCode.split(' ').filter(t => t !== '').slice(1,2).pop().split('-')
          icons.push(ccLicenseIcons.CC)
          ccTerms.forEach(term => {
            if (ccLicenseIcons[term]) icons.push(ccLicenseIcons[term])
          })
          licenseUrl = licenseUrl || `https://creativecommons.org/licenses/${ccTerms.join('-').toLowerCase()}/${ccVersion}`
          licenseIcons = icons
        }
      }
      this.licenseUrl = licenseUrl
      this.licenseIcons = licenseIcons
    },
    parseManifest(x){
      var html = "<table style='max-width:100%;table-layout: fixed;'><tbody style='background:none;font-size: 0.8rem;padding: 5px;'>";
      let content = {};
      let manifest = x;

      if (this.manifests.length != 0){
        if (manifest.attribution) { content['attribution'] = manifest.attribution }
        if (manifest.description) { content['description'] = manifest.description }
        if (manifest.label) { content['label'] = manifest.label.en ? manifest.label.en[0] : manifest.label }
        if (manifest.metadata){
          manifest.metadata.forEach(message => {
            if (!content[message['label']] && message['label'] != 'mode' && message['label'] != 'repo' && message['label'] != 'acct' && message['label'] != 'essay' && message['label'] != 'title_formatted'){
            }
          })
        }
        let itemInfo = this.findItem({type:'Annotation', motivation:'painting'}, manifest, x.seq || 1).body
        if (itemInfo){
          content['image format'] = itemInfo.format
          content['image height'] = itemInfo.height
          content['image width'] = itemInfo.width
        }
        content['IIIF id'] = manifest.id

        for(var key in content){
          
            html+= '<tr style="background:none; padding: 0px">';
            html+= '<td style="background:none; padding: 5px;max-width: 200px;overflow: auto;">' + key + '</td>';
            if (key == 'license' && this.license && this.licenseUrl){
              html += '<td style="background:none; padding: 5px;max-width: 200px;overflow: auto;">' + 
                      '<span v-if="licenseUrl" class="licenses"><a :href="licenseUrl" target="_blank"><i v-for="(icon, idx) in licenseIcons" :key="idx" :class="icon"></i></a></span></td>';
            }
            else {
              html+= '<td style="background:none; padding: 5px;max-width: 200px;overflow: auto;">' + content[key]+ '</td>';
            }
            html+= '</tr>';
        }
        html+='</tbody></table>';
      }

      return html;
    },
    displayInfoBox() {

      if (this.manifests.length == 2 && (this.mode === 'layers' || this.mode === 'curtain')){
        if (this.sliderPct < 50){
          this.imageInfo = this.parseManifest(this.manifests[0])
        }
        else if (this.sliderPct > 50){
          this.imageInfo = this.parseManifest(this.manifests[1])
        }
      } else {
        if (this.currentItem) {
          this.imageInfo = this.parseManifest(this.currentItem);
        }
        else {
          this.imageInfo = this.parseManifest({...this.manifests[0], ...this.viewerItems[0]});
        }
      }

      if (!this.tippy) {
        new tippy(document.querySelectorAll('.info-box'), {
          animation:'scale',
          trigger:'click',
          interactive: true,
          allowHTML: true,
          placement: 'bottom-start',
          zIndex: 11,
          preventOverflow: { enabled: true },
          hideOnClick: true,
          
          onShow: (instance) => {
            instance.setContent(this.imageInfo)
          },
          onHide(instance) {
            instance.setProps({trigger: 'mouseenter'});
          }
        })
      }
    
    }
  },       
  watch: {
    isAuthenticated() {
      if (this.annotator) this.annotator.readOnly = !this.isAuthenticated
    },
    license: {
      handler: function () {
        this.evalLicense()
      },
      immediate: true
    },
    height() {
      this.goHome(true)
    },
    width() {
      this.goHome(true)
    },
    selected(current, prior) {
      if (prior === 'imageViewer') {
          this.actionSources.forEach(elem => elem.classList.remove('image-interaction'))
      }
      if (prior && current === 'imageViewer') {
        this.$nextTick(() => {
          this.actionSources.forEach(elem => elem.classList.add('image-interaction'))
          setTimeout(() => this.goHome(true), 1)
        })
      }
    },
    viewerIsActive: {
      handler: function (isActive) {
        if (isActive) {
          if (!this.viewer) this.initViewer()
          this.loadManifests(this.viewerItems).then(manifests => this.manifests = manifests)
        }
      },
      immediate: false
    },
    viewerItems (current, previous) {
      const cur = current.map(item => this.stringifyKeysInOrder(item))
      const prev = previous ? previous.map(item => this.stringifyKeysInOrder(item)) : []
      if (this.viewer && this.viewerIsActive) {
        if (cur.join() !== prev.join()) {
          this.loadManifests(this.viewerItems).then(manifests => this.manifests = manifests)
        } else {
          this.page = 0
          this.currentItem = { ...this.manifests[this.page], ...current[this.page] }
        }
      }
    },
    manifests(manifests) {
      if (manifests) {
        this.tileSources = this.manifests.map((manifest, idx) => {
          let found = this.findItem({type:'Annotation', motivation:'painting'}, manifest, this.viewerItems[idx]?.seq || 1)
          let itemInfo = found.body
          let tileSource = itemInfo.service
            ? `${(itemInfo.service[0].id || itemInfo.service[0]['@id'])}/info.json`
            : { url: itemInfo.id, type: 'image', buildPyramid: true }
          const opacity = idx === 0 ? 1 : this.mode === 'layers' ? 0 : 1
          return { tileSource, opacity }
        })
        this.loadTileSources()
        this.displayInfoBox()

        this.page = 0
        this.currentItem = { ...this.manifests[this.page], ...this.viewerItems[this.page] }
      }
    },
    page() {
      this.currentItem = { ...this.manifests[this.page], ...this.viewerItems[this.page] }
      if (this.goToRegionCoords != null){
        this.$nextTick(() => {
          this.gotoRegion(this.goToRegionCoords)
          this.goToRegionCoords = null;
        })
      }
    },
    actions: {
      handler: function (actions) {
        if (actions[this.$options.name]) actions[this.$options.name].forEach(action => this.handleEssayAction(action))
      },
      immediate: true
    },
    actionSources: {
      handler: function (current, prior) {
        current.forEach(elem => elem.classList.add('image-interaction'))
        if (prior) prior.forEach(elem => elem.classList.remove('image-interaction'))
      },
      immediate: true
    },
    currentItem(current, previous) {
      this.annotations = []
      this.annoCursor = 0
      this.displayInfoBox()
    },
    currentItemSourceHash() { 
      this.loadAnnotations()
    },
    mode() {
      if (this.viewer) this.initViewer()
    },
    showAnnotationsNavigator(show) {
      if (show) {
        if (this.showAnnotations) this.showAnnotations = false
        this.gotoAnnotationSeq()
      } else {
        this.goHome()
      }
    },
    showAnnotations(show) {
      Array.from (document.querySelectorAll('.a9s-annotationlayer')).forEach(elem => elem.style.display = show ? 'unset' : 'none')
      if (!show && !this.showAnnotationsNavigator) setTimeout(() => this.goHome(true), 10)
    },
    annotatorEnabled: {
      handler: function (annotatorIsEnabled) {
        this.setAnnotatorEnabled(annotatorIsEnabled)
      },
      immediate: false
    },
    sliderPct() {
      const numItems = this.viewer.world.getItemCount()
      if (this.mode === 'layers') {
        if (numItems > 1) {
          const opacity = this.sliderPct/100
          this.viewer.world.getItemAt(0).setOpacity(1.0 - opacity)
          this.viewer.world.getItemAt(1).setOpacity(opacity)
          this.displayInfoBox()
        }
      } else if (this.mode === 'curtain') {
        const numItems = this.viewer.world.getItemCount()
        if (numItems > 1) {
          const foregroundImg = this.viewer.world.getItemAt(0)
          const backgroundImg = this.viewer.world.getItemAt(1)
          const fsize = foregroundImg.getContentSize()
          const bsize = backgroundImg.getContentSize()
          foregroundImg.setClip(new OpenSeadragon.Rect(this.sliderPct/100*fsize.x, 0, fsize.x, fsize.y))
          backgroundImg.setClip(new OpenSeadragon.Rect(0, 0, this.sliderPct/100*bsize.x, bsize.y))
          this.displayInfoBox()
        }
      }
    }
  }
}
</script>

<style>

  .a9s-annotationlayer {
    display: none;
    visibility: hidden;
    opacity: 0;
    transition: all 1s ease-out;
  }
  .r6o-widget.comment .lastmodified {
    display: none !important;
  }
  .image-viewer:hover .a9s-annotationlayer {
    visibility: visible;
    opacity: 1;
    transition: all 1s ease-in;
  }

  .image-interaction {
      border-bottom: 2px solid #444A1E;
      cursor: pointer;
      z-index: 10;
  }
  .image-interaction:hover {
      background: #a8e2bb !important;
      transition: all 0.2s ease-in;
  }

</style>

<style scoped>

  .openseadragon-container > div:nth-of-type(2) {
    margin: 8px 24px !important;
  }

    .osd {
      /* row-start / column-start / row-end / column-end */
      grid-area: 1 / 1 / 5 / 3; 
      width: 100%;
      height: 100%;
      background: gray;
    }

    .controls {
      grid-area: 3 / 2 / 2 / 3;
      width: 40px;
      margin-right: 20px;
      display: grid;
      align-self: start;
      cursor: pointer;
      z-index: 2;
      background: white;
      border-radius: 4px;
    }

    .slider {
      grid-area: 3 / 1 / 4 / 3; 
      width: 95%;
      justify-self: center;
      align-self: center;
      z-index: 2;
      margin-bottom: 10px;
      background-color: #a1a1a1 !important;
      opacity: 0.7;
    }
    .slider:hover {
      opacity: 1 !important;
    }
    .slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      background: #5b5c5e !important;
      cursor: pointer;
    }

    .annotations {
      display: grid;
      grid-template-rows: auto 1fr;
      grid-template-columns: 1fr;
      grid-area: 4 / 1 / 5 / 3;
      background-color: #272727;
      color: white;
      text-align: center;
      padding: 8px;
      z-index: 2;
    }

    .anno-controls {
      grid-area: 1 / 1 / 2 / 2;
      justify-self: stretch;
      display: grid;
      grid-template-columns: auto auto auto;
      cursor: pointer;
      align-items: center;
    }

    .anno-nav {
      grid-area: 1 / 2 / 2 / 3;
      justify-self: center;
      display: grid;
      grid-template-columns: auto auto auto;
      grid-gap: 20px;
    }
    .anno-close {
      grid-area: 1 / 2 / 2 / 4;
      justify-self: end;
    }
    .anno-close svg {
      font-size: 1rem !important;
    }
    .anno-controls-text {
      font-size: 0.8rem;
      margin-top: 0;
    }
    .anno-controls svg {
      font-size: 1rem;
      color: #fff;
      margin-top: 0;
    }
    .anno-controls svg:hover {
      color: #444A1E;
    }

    .annos {
      grid-area: 2 / 1 / 3 / 2;
      padding: 8px;
      max-height: 90px;
      overflow-y: scroll;
    }

    .citation {
      grid-area: 5 / 1 / 6 / 3;
      z-index: 1;
      justify-self: stretch;
      /*align-self: stretch;*/
      max-height: 50px;
      overflow: auto;
      /* background-color: rgba(255, 255, 255, 0.8); */
      background-color: #ccc;
      padding: 9px 6px;
      text-align: center;
      line-height: 1;
    }

    .viewport-coords {
      grid-area: 1 / 1 / 2 / 2;
      width: 130px;
      height: 20px;
      padding: 3px 6px;
      font-size: 0.8rem;
      cursor: pointer;
      background-color: rgba(255, 255, 255, 0.5);
      z-index: 2;
    }

    .image-viewer {
      display: grid;
      width: 100%;
      height: 100%;
      grid-template-rows: 20px 1fr auto auto auto;
      grid-template-columns: 1fr 60px;
      font-family: Roboto, sans-serif;
      font-size: 1.0rem;
      line-height: 1.4rem;
      scroll-behavior: smooth;
      color: #000;
    }

    .controls svg {
      color: black;
      width: 100%;
      font-size: 18px;
      margin-top: 12px;
    }

    .controls span {
        line-height: 2;
        border-bottom: 1px solid #989898;
    }

    .controls span:last-child {
      border-bottom: none;
    }

    .controls span:hover, .controls svg:hover {
        color: #444A1E;
        fill: #444A1E;
        transform: scale(1.05, 1.05);
    }

    .auto-hide {
      visibility: hidden;
      opacity: 0;
      transition: all 1s ease-out;
    }

    .image-viewer:hover .controls,
    .image-viewer:hover .slider,
    .image-viewer:hover .annotations,
    .image-viewer:hover .viewport-coords,
    .image-viewer:hover .citation {
      visibility: visible;
      opacity: 1;
      transition: all 0.3s ease-in;
    }

    .slider {
      -webkit-appearance: none;
      height: 5px;
      border-radius: 5px;  
      background: #d3d3d3;
      outline: black;
      opacity: 0.7;
      -webkit-transition: .2s;
      transition: opacity .2s;
    }
    .slider:hover {
      opacity: 1;
    }

    .slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 15px;
      height: 15px;
      border-radius: 50%; 
      background: beige;
      cursor: pointer;
    }

    .slider::-moz-range-thumb {
      width: 15px;
      height: 15px;
      border-radius: 50%;
      background: beige;
      cursor: pointer;
    }

    .image-label {
      font-size: 0.9rem;
      font-weight: bold;
    }

    .attribution {
        font-size: 0.7rem;
    }

    .licenses {
      font-size: 12px;
    }

    .licenses svg {
      margin-left: 4px;
    }
    .tippy-content {
      font-family: Roboto !important;
      font-size: 1rem;
      display: table;
    }

    table td th{
      background:none;
      font-size: 0.8rem;
      padding: 5px;
    }
    .info-box-content{
      display: flex;
    }

    .info-box {
      z-index: 11,
    }
    

</style>
