<template>
    <div id="datavis" :style="containerStyle" />
</template>

<script>

/* global d3plus */

// Uses https://d3plus.org/

const dependencies = [
    'https://d3plus.org/js/d3.min.js',
    'https://d3plus.org/js/d3plus.min.js',
    'https://d3plus.org/js/d3plus-network.v0.6.full.min.js'
]

module.exports = {
    name: 've-d3plus-network',
    props: {
      items: Array,
      width: Number,
      height: Number
    },
    computed: {
      containerStyle() { return { width: `${this.width}px`, height: `${this.height}px`, overflowY: 'auto !important', marginLeft: '24px' } },
      item() { return this.items.length > 0 ? this.items[0] : {} }
    },
    mounted() {
        console.log(this.$options.name, this.items)
        if (typeof d3plus === 'object') {
            this.init()
        } else {
            this.loadDependencies(dependencies, 0, this.init)
        }
    },
    methods: {
        init() {
            fetch(this.item.url).then(resp => resp.text())
            .then(delimitedDataString => {
                const data = this.transformData(this.delimitedStringToObjArray(delimitedDataString))
                console.log(data)
                new d3plus.Network() // eslint-disable-line no-undef
                    .select('#datavis')
                    .links(data.edges)
                    .nodes(data.nodes)
                    .render()
            })
        },
        transformData(objArray) {
            const nodes = {}
            const transformed = { nodes: [], edges: [] }
            objArray.forEach((obj) => {
                ['source', 'target'].forEach((nodeType) => {
                let nodeId = obj[nodeType].id || obj[nodeType].label
                if (nodes[nodeId] === undefined) {
                    let id = transformed.nodes.length
                    // let qid = obj[nodeType].id[0] === 'Q' ? obj[nodeType].id : undefined
                    let label = obj[nodeType].label || obj[nodeType].id
                    nodes[nodeId] = id
                    transformed.nodes.push({ id: label })
                }
                });
            });
            objArray.forEach((obj) => {
                transformed.edges.push({
                    source: nodes[obj.source.id || obj.source.label],
                    target: nodes[obj.target.id || obj.target.label]
                })
            })
            return transformed;
        }
    },
    watch: {
    items() {
      console.log(`${this.$options.name}.watch.items`, this.items)
      this.init()
    }
    }
  }
</script>

<style scoped>
  body {
    margin: 0;
    /* overflow: hidden; */
  }
</style>
