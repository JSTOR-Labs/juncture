<template>
  <div class="osd" id="ps-osd" :style="containerStyle">
  
      <div class="citation">
        <span v-if='title || label || description' v-html="title || label || description" class="image-label"></span><br>
        <span v-if="attribution" v-html="attribution" class="attribution"></span>
      </div>

  </div>
</template>

<script>

const sparqlEndpoint = 'https://cy9in0xsv5.execute-api.us-east-1.amazonaws.com/prod/sparql'
const iiifService = 'https://iiif.juncture-digital.org'
// const iiifService = 'http://localhost:8888'

const sparql = `
  PREFIX jwd: <http://kg.jstor.org/entity/>
  PREFIX jwdt: <http://kg.jstor.org/prop/direct/>
  PREFIX jp: <http://kg.jstor.org/prop/>
  PREFIX jps: <http://kg.jstor.org/prop/statement/>
  PREFIX jpq: <http://kg.jstor.org/prop/qualifier/>
  PREFIX wd: <http://www.wikidata.org/entity/>
  PREFIX wdt: <http://www.wikidata.org/prop/direct/>
  PREFIX schema: <http://schema.org/>

  CONSTRUCT {
    ?specimen jwdt:P1660 ?specimenOf ;
              schema:description ?description ;
              rdf:type jwd:Q14316 ;
              jwdt:P1663 ?collectionDate ;
              jwdt:P1662 ?collector ;
              jwdt:P1665 ?locationCollected ;
              jwdt:P1106 ?jstorPlantsId ;
              jwdt:P1661 ?specimenType ;
              jwdt:P501 ?taxonName ;
              jwdt:P1666 ?availableAt ;
              jp:P1467 ?img .
    ?img jps:P1467 ?url ; jpq:P1669 ?imgSize .
    ?availableAt jps:P1666 ?wdID ; rdfs:label ?herbariumName .
    ?locationCollected jps:P1665 ?locId ; rdfs:label ?locationName ; wdt:P6766 ?wofId .
  } WHERE {
    ?specimen jwdt:P17 jwd:Q14316 ;
            <<SELECTOR>>
            schema:description ?description ;
            jwdt:P1106 ?jstorPlantsId ;
            jwdt:P501 ?taxonName ;
            jp:P1467 [ jps:P1467 ?img ;
                       jpq:P1669 ?imgSize ] .
    FILTER(?imgSize = 'best')
    OPTIONAL { ?specimen jwdt:P1661 ?specimenType . }
    OPTIONAL { ?specimen jwdt:P1660 ?specimenOf . }
    OPTIONAL { ?specimen jwdt:P1663 ?collectionDate . }
    OPTIONAL { ?specimen jwdt:P1662 ?collector . }
    OPTIONAL {
        ?specimen jwdt:P1665 ?locationCollected .
        SERVICE <https://query.wikidata.org/sparql> {
            ?locationCollected rdfs:label ?locationName .
            FILTER(LANG(?locationName) = 'en')
            OPTIONAL { ?locationCollected wdt:P6766 ?wofId . }
        }
    }        
    OPTIONAL {
        ?specimen jwdt:P1666 ?availableAt .
        SERVICE <https://query.wikidata.org/sparql> {
            ?availableAt rdfs:label ?herbariumName .
            FILTER(LANG(?herbariumName) = 'en')
        }
    }
  }
  LIMIT <<LIMIT>>
`

const context = {
  "@context": {
    "jwd": "http://kg.jstor.org/entity/",
    "jwdt": "http://kg.jstor.org/prop/direct/",
    "jp": "http://kg.jstor.org/prop/",
    "jps": "http://kg.jstor.org/prop/statement/",
    "jpq": "http://kg.jstor.org/prop/qualifier/",
    "rdfs":  "http://www.w3.org/2000/01/rdf-schema#",
    "schema": "http://schema.org/",
    "wd": "http://www.wikidata.org/entity/",
    "wdt": "http://www.wikidata.org/prop/direct/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",

    "Specimen": "jwd:Q14316",

    "id": "@id",

    "collectionDate": {
        "@id": "jwdt:P1663",
        "@type": "xsd:dateTime"
    },
    "collector": {
        "@id": "jwdt:P1662",
        "@container": "@set"
    },
    "description": {
        "@id": "schema:description",
        "@language": "en"
    },
    "herbarium": {
        "@id": "jwdt:P1666",
        "@type": "@id"
    },
    "images": {
        "@id": "jp:P1467",
        "@type": "@id",
        "@container": "@set"
    },
    "imgSize": {
        "@id": "jpq:P1669"
    },
    "instance of": {
        "@id": "jwdt:P17",
        "@type": "@id"
    },
    "jstorPlantsId": {
        "@id": "jwdt:P1106"
    },
    "locationCollected": {
        "@id": "jwdt:P1665"
    },
    "label": {
        "@id": "rdfs:label",
        "@language": "en"
    },
    "specimenOf": {
        "@id": "jwdt:P1660",
        "@type": "@id"
    },
    "specimenType": {
        "@id": "jwdt:P1661"
    },
    "taxonName": {
        "@id": "jwdt:P501"
    },
    "wofId": {
        "@id": "wdt:P6766"
    }
  }
}

module.exports = {
  name: 've-plant-specimen',
  props: {
    items: { type: Array, default: () => ([]) },
    viewerIsActive: Boolean
  },
  data: () => ({
    viewerLabel: 'Plant Specimen',
    viewerIcon: 'fas fa-seedling',
    

    dependencies: [
      'https://cdn.jsdelivr.net/npm/jsonld@1.0.0/dist/jsonld.min.js',
      'https://cdn.jsdelivr.net/npm/openseadragon@2.4/build/openseadragon/openseadragon.min.js'],
      viewer: null,
      tileSources: []
  }),
  computed: {
    specimenItems() { return this.items.filter(item => item[this.componentName]) },
    max() {
      let withMax = this.specimenItems.filter(item => item.max)
      return withMax.length > 0 ? parseInt(withMax[0].max) : 10
    },
    containerStyle() { return { height: this.viewerIsActive ? '100%' : '0' } },
    attribution() { return this.items[0] ? this.items[0]['attribution'] : null },
    title() { return this.items[0] ? this.items[0]['title'] : null },
    label() { return this.items[0] ? this.items[0]['label'] : null },
    description() { return this.items[0] ? this.items[0]['description'] : null },
  },
  mounted() { this.loadDependencies(this.dependencies, 0, this.init) },
  methods: {

    init() {
      this.initOsdViewer()
      this.findSpecimens()
    },

    async findSpecimens() {
      let promises = this.specimenItems.map(item => {
        let selector
        if (item.jpid) selector = `jwdt:P1106 "${item.jpid}" ;`
        else if (item.eid || item.wdid) selector = `jwdt:P1660 <http://www.wikidata.org/entity/${item.eid || item.wdid}> ;`
        else selector = `jwdt:P501 "${item['taxon-name']}" ;`
        return this.doSparqlQuery(sparql.replace(/<<SELECTOR>>/, selector).replace(/<<LIMIT>>/, this.max))
      })
      let foundForItems = await Promise.all(promises)
      let flattened = []
      foundForItems.map(item => item['@graph']).forEach(specimens => { flattened = [...flattened, ...specimens] })

      promises = flattened.map(specimen => {
        return fetch(`${iiifService}/manifest/`, {
            method: 'POST',
            headers: {'Content-type': 'application/json'},
            body: JSON.stringify(this.metadata(specimen))
          }).then(resp => resp.json())
        })
      let manifests = await Promise.all(promises)
      this.tileSources = manifests.map(manifest => {
        return manifest.sequences[0].canvases[manifest.seq || 0].images[0].resource.service
          ? `${manifest.sequences[0].canvases[manifest.seq || 0].images[0].resource.service['@id']}/info.json`
          : { url: manifest.sequences[0].canvases[manifest.seq || 0].images[0].resource['@id'] || manifest.metadata.find(md => md.label === 'source').value,
              type: 'image', buildPyramid: true }
      })
    },

    initOsdViewer() {
      if (this.viewer) this.viewer.destroy()
      this.$nextTick(() => {
        this.viewer = OpenSeadragon({
          id: 'ps-osd', prefixUrl: 'https://openseadragon.github.io/openseadragon/images/',
          sequenceMode: true,
          showReferenceStrip: true,
          // homeFillsViewer: true,
        })
      })
    },

    async doSparqlQuery(query) {
      let resp = await fetch(sparqlEndpoint, {
        method: 'POST', body: new URLSearchParams({query}),
        headers: { Accept: 'text/plain', 'Content-type': 'application/x-www-form-urlencoded' }
      })
      let rdf = await resp.text()
      let jld = await jsonld.fromRDF(rdf, { format: 'application/n-quads' })
      return jsonld.frame(jld, frame = {'@context': context, '@type': 'Specimen'})
    },

    metadata(specimen) {
      let bestImgUrl = specimen.images.find(img => img.imgSize === 'best').id
      let rftId = bestImgUrl.match(/rft_id=([^&]*)/)[1]
      let data = {url: `${iiifService}/gp-proxy${rftId}`}
      if (specimen.taxonName) data['Taxon name'] = specimen.taxonName
      if (specimen.jstorPlantsId) data['Global Plants ID'] = specimen.jstorPlantsId
      if (specimen.description) data['Description'] = specimen.description
      if (specimen.description) data['Label'] = specimen.description
      if (specimen.specimenType) data['Specimen type'] = specimen.specimenType
      if (specimen.collector) data['Collector'] = specimen.collector.join('; ')
      if (specimen.locationCollected) data['Location collected'] = specimen.locationCollected.label
      if (specimen.collectionDate) data['Date collected'] = specimen.collectionDate
      if (specimen.herbarium) data['Herbarium'] = specimen.herbarium.label
      return data
    }

  },
  watch: {
    specimenItems: {
      handler: function () {
        this.findSpecimens()
      },
      immediate: true
    },
    tileSources: {
      handler: function () {
        if (this.viewer) this.viewer.open(this.tileSources)
      },
      immediate: true
    }
  }
}

</script>

<style>
</style>