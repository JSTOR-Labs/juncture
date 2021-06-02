<template>

  <div>
  
    <div id="essay-component" ref="essay" v-html="processedHtml"></div>

    <!-- Entity infobox popup -->
    <div style="display:none;">
      <div ref="popup" class="popup" v-if="hoverEntity">
        <div v-if="hoverEntity.thumbnails" class="image"><img :src="hoverEntity.thumbnails[0]"></div>
        <div class="label" v-html="hoverEntity.label"></div>
        <div v-if="hoverEntity.description" class="description" v-html="hoverEntity.description"></div>
        <div v-if="hoverEntity.summary" class="summary" v-html="hoverEntity.summary"></div>
      </div>
    </div>

  </div>

</template>

<script>

module.exports = {  
  name: 'Essay',
  props: {
    html: { type: String, default: '' },
    path: String,
    anchor: String,
    entities: { type: Object, default: () => ({}) },
    params: { type: Array, default: () => ([]) },
    availableViewers: { type: Array, default: () => ([]) },
    scrollTop: { type: Number, default: 0 },
  },
  data: () => ({
    processedHtml: '',
    hoverEntity: null,
    active: null
  }),
  computed: {
    items() { return this.active ? this.paramsInScope(document.querySelector(`[data-id="${this.active}"]`)) : [] },
  },
  mounted() {},
  methods: {

    // Convert essay Markdown into HTML.  Markdown headings are used to infer content heirarchy
    toElem(html) {
      let essay = document.createElement('div')
      let tmp = new DOMParser().parseFromString(html, 'text/html').children[0].children[1]
      let currentSection = essay
      let segments = []
      let segment

      Array.from(tmp.children).forEach(el => {
        if (el.tagName[0] === 'H' && isNumeric(el.tagName.slice(1))) {
          let sectionLevel = parseInt(el.tagName.slice(1))
          if (segments) {
            segments.forEach(segment => currentSection.innerHTML += segment.outerHTML)
            segments = []
            segment = null
          }
          currentSection = new DOMParser().parseFromString('<section></section>', 'text/html').children[0].children[1].children[0]
          let elClasses = Array.from(el.classList)
          el.classList.remove(...elClasses)
          if (!el.innerHTML) el.style.display = 'none'
          currentSection.innerHTML += el.outerHTML

          let headings = [...essay.querySelectorAll(`H${sectionLevel-1}`)]
          let parent = sectionLevel === 1 || headings.length === 0 ? essay : headings.pop().parentElement
          let parentDataID = parent.dataset.id || ''
          let sectionSeq = parent.querySelectorAll(`H${sectionLevel}`).length
          let currentDataID = parentDataID ? `${parentDataID}.${sectionSeq}` : sectionSeq
          currentSection.setAttribute('data-id', currentDataID)

          if (elClasses.indexOf('cards') >= 0) {
            currentSection.appendChild(new DOMParser().parseFromString('<section class="cards"></section>', 'text/html').children[0].children[1].children[0])
          } else {
            currentSection.classList.add(...elClasses)
            let cardsWrapper = parent.querySelector(':scope > .cards')
            if (cardsWrapper) {
              currentSection.classList.add('card')
              parent = cardsWrapper
            }
          }

          parent.appendChild(currentSection)

        } else if (el.tagName === 'P') {
          if (el.innerHTML.indexOf('ve-button.png') >= 0) {
            el = null
          } else if (el.innerHTML.indexOf('class="nav"') >= 0) {
            currentSection.innerHTML += el.innerHTML
          } else {
            segment = new DOMParser().parseFromString('<div></div>', 'text/html').children[0].children[1].children[0]
            segment.setAttribute('data-id', `${currentSection.dataset.id}.${segments.length + 1}`)
            segment.classList.add('segment')
            segment.innerHTML = el.outerHTML
            segments.push(segment)
          }
        } else if (el.tagName === 'SECTION' && el.className === 'footnotes') {
          currentSection.innerHTML += el.outerHTML
        } else {
          if (segment) {
            segment.innerHTML += el.outerHTML
          } else {
            currentSection.innerHTML += el.outerHTML
          }
        }
      })
      if (segments) {
        segments.forEach(segment => currentSection.innerHTML += segment.outerHTML)
        segments = []
      }
      return essay
    },

    async essayLoaded() {
      this.active = null
      let essayElem = this.$refs.essay
      Array.from(essayElem.querySelectorAll('.collapsible')).forEach(el =>el.addEventListener('click', this.toggleExpandCollapse))
      let params = Array.from(essayElem.querySelectorAll('param'))
        .map(param => {
          let prior = param.previousElementSibling
          while (prior && prior.tagName !== 'P' && prior.tagName[0] !== 'H') {
            prior = prior.previousElementSibling
          }
          return { ...{ elem: prior ? prior.parentElement : essayElem }, ...attrsToObject(param) }
        })
        .map(param => {
          let viewerTag = Object.keys(param).find(attr => !attr.value && this.availableViewers.indexOf(attr) >= 0)
          if (viewerTag) param.viewer = viewerTag
          else if (!Object.keys(param).find(attr => attr.indexOf('ve-') === 0)) param['ve-entity'] = ''
          return param
        })
      this.$emit('set-params', params)
      let entitiesFromElem = this.findEntities(essayElem)
      let entities = await this.getEntityData(Object.keys(entitiesFromElem))
      this.$emit('set-entities', entities)
      this.$nextTick(() => {
        this.tagEntities(essayElem)
        this.addPopups(entities)
        this.convertLinks(essayElem)
        let segments = [...essayElem.querySelectorAll('.segment')]
        if (this.anchor) {
          let anchorElem = document.getElementById(this.anchor)
          if (anchorElem) {
            this.scrollTop = anchorElem.offsetTop
            essayElem.scrollTop = this.scrollTop - 100
          }
          this.anchor = null
        } else {
          essayElem.scrollTop = 0
          this.active = segments.length > 0 ? segments[0].dataset.id : null
        }
      })
    },

    doCustomFormatting(elem) {
      Array.from(elem.querySelectorAll('section.cards')).forEach(cardsSection => {
        Array.from(cardsSection.querySelectorAll('section')).forEach(card => {
          ['img', '.card > .segment > p > a', '.card > .segment > p > strong', 'ul'].forEach(selector => {
            let el = card.querySelector(selector)
            if (el) {
              if (selector !== 'strong' || el.parentElement.tagName !== 'A') card.appendChild(el)
            }
          })
          let segments = []
          Array.from(card.querySelectorAll('.segment')).forEach(seg => {
            if (seg.textContent.trim() === '') {
              card.removeChild(seg)
            } else {
              segments.push(seg)
            }
          })
          if (segments.length > 0) {
            let abstractWrapper = document.createElement('div')
            abstractWrapper.classList.add('abstract')
            card.appendChild(abstractWrapper)
            let abstractDiv = document.createElement('div')
            abstractDiv.classList.add('abstract-text')
            abstractWrapper.appendChild(abstractDiv)
            segments.forEach(seg => abstractDiv.appendChild(seg))
            abstractWrapper.innerHTML += '<button class="collapsible">read more</button>'
          }
        })
      })
      return elem.innerHTML
    },

    // Adds tippy popups to tagged entity text
    addPopups(entities) {
      tippy('.entity', {
        allowHTML: true,
        interactive: true,
        appendTo: document.body,
        delay: [null, null],
        placement: 'right',
        theme: 'light-border',
        onShow: async (instance) => {
          this.hoverEntity = this.entities[instance.reference.dataset.eid]
          if (this.hoverEntity.mwPage && !this.hoverEntity.summary) {
            let page = this.hoverEntity.mwPage.replace(/\/w\//, '/wiki/').split('/wiki/').pop()
            let resp = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${page}`)
            resp = await resp.json()
            entities[instance.reference.dataset.eid].summary = resp.extract_html
            this.$emit('set-entities', entities)
            this.hoverEntity = {...entities[instance.reference.dataset.eid]}
          }
          this.$nextTick(() => instance.setContent(this.$refs.popup.outerHTML))
        },
        onHide: () => {}
      })
    },

    // Converts link tags to elements with click listeners enabling intra-app navigation without page loading
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
            target = parsedUrl.hash === '' ? `/${pathElems.join('/')}/` : parsedUrl.hash.split('?')[0]
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
              if (anchorElem) {
                this.scrollTop = anchorElem.offsetTop
                this.$refs.essay.scrollTop = this.scrollTop - 100
              }
            } else {
              this.$emit('load-essay', path)
            }
          })
        } else {
          // If external link, add external link icon to text and force opening in new tab
          link.innerHTML += '<sup><i class="fa fa-external-link-square-alt" style="margin-left:3px;margin-right:2px;font-size:0.7em;color:#219653;"></i></sup>'
          link.setAttribute('target', '_blank')
        }
      })
    },

    convertResourceUrls(root) {
      root.querySelectorAll('img').forEach(img => {
        if (img.src.indexOf(window.location.origin) === 0) img.setAttribute('src', convertURL(img.src))
      })
      root.querySelectorAll('param').forEach(param => {
        ['url', 'banner'].forEach(attr => {
          if (param.attributes[attr]) param.setAttribute(attr, convertURL(param.attributes[attr].value, window.location.pathname, this.mdDir !== '/'))
        })
      })
      return root
    },

    // Finds all entity references in param tags
    findEntities(root) {
      let entities = Object.fromEntries(
        Array.from(root.querySelectorAll('param, span'))
          .filter(el => el.attributes.eid)
          .map(el => attrsToObject(el))
          .map(entity => [entity.eid, entity]))
        Array.from(root.querySelectorAll('param'))
          .filter(el => el.attributes.center && isEntityID(el.attributes.center.value))
          .filter(el => !entities[el.attributes.center.value])
          .map(el => { return {...attrsToObject(el), ...{eid: el.attributes.center.value }} })
          .forEach(entity => entities[entity.eid] = entity)
      return entities
    },

    // Gets labels, aliases, images and geo coords for referenced Wikdata entities
    async getEntityData(entityIds) {
      let values = entityIds.map(eid => `(<http://www.wikidata.org/entity/${eid}>)`).join(' ')
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
      let entities = {}
      resp.results.bindings.forEach(rec => {
        let eid = rec.item.value.split('/').pop()
        if (!entities[eid]) entities[eid] = {
            ...this.entities[eid], 
            ...{
              eid, 
              label: rec.label.value, 
              aliases: new Set(this.entities[eid] ? Array.from(this.entities[eid].aliases) : []),
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

    toggleExpandCollapse(e) {
      let button = e.target
      let textDiv = button.previousElementSibling
      if (button.innerText == 'read more') {
        button.innerText = 'read less'
        textDiv.style['-webkit-line-clamp'] = 'unset'
      }
      else if (button.innerText == 'read less') {
        button.innerText = 'read more'
        textDiv.style['-webkit-line-clamp'] = 5
      }
    },

    // Finds all param tags in elements between top-level app element and element in para arg
    paramsInScope(para) {
      let paramTags = []
      let scope = []
      let el = para
      while (el && el.id !== 'app') {
        scope.push(el)
        el = el.parentElement
      }
      scope.forEach(elemInScope => 
        paramTags = [...paramTags, ...this.params.filter(param => param.elem === elemInScope)]
      )
      return paramTags
    },

    // Finds words/phrases in content paragraphs that match labels or aliases for entities in scope
    // Matched text is wrapped with a span tag for reacting to hover and click actions
    tagEntities(root) {
      Array.from(root.querySelectorAll('.segment p')).forEach(para => {
        let paraHTML = para.innerHTML
        this.paramsInScope(para, this.params).filter(param => param['ve-entity'] !== undefined && param.eid !== undefined).map(param => param.eid).forEach(eid => {
          let entity = this.entities[eid]
          if (entity) {
            let toMatch = [...[entity.label], ...entity.aliases.filter(alias => alias.length > 3)]
            for (let i = 0; i < toMatch.length; i++) {
              let re = new RegExp(`[\\s(](${toMatch[i].replace(/'/, "'?")})[\\s);:,.]`, 'i')
              let match = re.exec(paraHTML)
              if (match) {
                paraHTML = paraHTML.replace(match[1], `<span class="entity inferred" data-eid="${eid}">${match[1]}</span>`)
                entity.foundIn.add(para.parentElement.dataset.id)
                break
              }
            }
          }
        })
        para.innerHTML = paraHTML
      })
      Array.from(root.querySelectorAll('p span')).forEach(span => {
        if (span.attributes.eid) {
          span.setAttribute('data-eid', span.attributes.eid.value)
          span.classList.add('entity', 'tagged')
        }
      })
      Array.from(root.querySelectorAll('span.entity'))
        .forEach(el => el.addEventListener('click', (e) => {
          console.log('entity selected', e.target.dataset.eid)
        })
      )
    },

  },
  watch: {

    html: {
      handler: function (html) {
        if (html) {
          let elem = this.toElem(html)
          elem = this.convertResourceUrls(elem)
          this.processedHtml = this.doCustomFormatting(elem)
          this.$nextTick(() => this.essayLoaded())
        }
      },
      immediate: true
    },

    active: {
      handler: function (current, prior) {
        console.log(`activeSegment=${current}`)
        this.$emit('set-active', current)
        let activeSegment = document.querySelector(`[data-id="${current}"]`)
        if (activeSegment) activeSegment.classList.add('active')
        let priorSegment = document.querySelector(`[data-id="${prior}"]`)
        if (priorSegment) priorSegment.classList.remove('active')
      },
      immediate: true
    },

    items: {
      handler: function (items) {
        console.log('Essay.items', items)
        this.$emit('set-items', items)
      },
      immediate: true
    },

    scrollTop: {
      handler: function (pos) {
        if (pos) {
          let target = this.$refs.essay
          let segments = Array.from(target.querySelectorAll('.segment'))
          let i
          for (i = 0; i < segments.length; i++) {
            if (pos <= segments[i].offsetTop + segments[i].clientHeight - 200) break
          }
          if (i < segments.length && this.active !== segments[i].dataset.id ) this.active = segments[i].dataset.id
        }
      },
      immediate: true
    }

  }
}

</script>

<style>
</style>