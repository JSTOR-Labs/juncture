<template>
    <div id="table" :style="containerStyle"></div>
</template>

<script>

/* global Tabulator */

// A wrapper for http://tabulator.info/
const viewerLabel = 'Table Viewer'
const viewerIcon = 'fas fa-table'
const dependencies = [
    'https://unpkg.com/tabulator-tables@4.9.1/dist/css/tabulator.min.css',
    'https://unpkg.com/tabulator-tables@4.9.1/dist/js/tabulator.min.js'
]

module.exports = {
    name: 've-tabulator',
    props: {
      items: Array,
      viewerIsActive: Boolean,
      width: Number,
      height: Number
    },
    data: () => ({
        viewerLabel,
        viewerIcon,
        dependencies
    }),
    computed: {
        containerStyle() { return { width: `${this.width}px`, height: this.viewerIsActive ? '100%' : '0'} },
        filteredItems() { return this.items.filter(item => item[this.componentName]) },
        input() { return this.filteredItems[0].data || this.filteredItems[0].url }
    },
    mounted() {
        this.loadDependencies(dependencies, 0, this.init)
    },
    methods: {
        init() {
            fetch(this.input).then((resp) => resp.text())
            .then((delimitedDataString) => {
                const delimiter = this.input.split('.').pop() == 'tsv' ? '\t' : ',';
                const data = this.toObjArray(delimitedDataString, delimiter)
                new Tabulator('#table', {
                    data: data.objs, 
                    height: this.height,
                    layout: 'fitColumns',
                    columns: data.fields.map(field => { return { title: field, field }})
                })
            })
        },
        // Converts a delimited (CSV or TSV) file into a javascript object array
        //   The first row is assumed to include column names which are used as object keys
        toObjArray(delimitedData, delimiter) {
            const data = { fields: [], objs: [] }
            delimiter = delimiter || '\t'
            const lines = delimitedData.split('\n').filter(line => line.trim() !== '')
            if (lines.length > 1) {
                data.fields = lines[0].split(delimiter).map(key => key.trim());
                lines.slice(1).forEach(line => {
                    let obj = {}
                    line.split(delimiter)
                        .map(value => value.trim())
                        .forEach((value, i) => obj[data.fields[i]] = value)
                    data.objs.push(obj)
                })
            }
            return data
        }
    }
  }
</script>

<style scoped>
</style>
