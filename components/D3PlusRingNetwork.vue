<template>
    <div id="datavis" :style="containerStyle"></div>
</template>

<script>

/* global d3plus */

// Uses https://d3plus.org/

const viewerLabel = 'Network Viewer'
const viewerIcon = 'fas fa-project-diagram'
const dependencies = [
    // 'https://fonts.googleapis.com/css?family=Roboto',
    // 'https://d3plus.org/css/styles.css?v=3',
    // 'https://d3plus.org/js/d3.min.js',
    // 'https://d3plus.org/js/d3plus.min.js',
    // 'https://d3plus.org/js/d3plus-network.v0.6.full.min.js',
    'https://cdn.jsdelivr.net/npm/d3plus@2'
]

module.exports = {
    name: 've-d3plus-ring-network',
    props: {
      items: Array,
      viewerIsActive: Boolean,
      width: Number,
      height: Number
    },
    data: () => ({
    viewerLabel,
    viewerIcon,
    dependencies,
    }),
    computed: {
      filteredItems() { return this.items.filter(item => item[this.componentName]) },
      item() { return this.filteredItems.length > 0 ? this.filteredItems[0] : {} },
      containerStyle() { return { 
          width: `${this.width}px`,
          height: this.viewerIsActive ? `${this.height}px` : '0',
          overflowY: 'auto !important', 
          marginLeft: '24px',
          backgroundColor: this.items[0] ? this.items[0].background || 'white' : 'white'
        }
      },
    },
    mounted() {
        // console.log(this.$options.name, this.items)
        if (typeof d3plus === 'object') {
            this.init()
        } else {
            this.loadDependencies(dependencies, 0, this.init)
        }
    },
    methods: {
        init() {
            var links;
            fetch(this.item.url).then(resp => resp.text())
            .then(delimitedDataString => {
                links = this.delimitedStringToObjArray(delimitedDataString)
                    .map(item => { return { source: item.source.label, target: item.target.label } })
            })
            .then(() => {
                //remove old viscontent DOM object
                var oldObj = document.getElementById("viscontent");
                if (oldObj){
                    oldObj.remove();
                }

                //add new viscontent DOM object
                var newDiv = document.createElement("div");
                newDiv.setAttribute('id', 'viscontent');
                document.getElementById("datavis").appendChild(newDiv)

                var viz = new d3plus.Rings() // eslint-disable-line no-undef
                    .select('#viscontent')
                    .links(links)
                    .label(d => d.id)
                    .center(this.item.center)
                
                viz.render()
            });
        }
    },
    watch: {
        items() {
            this.init()
        }
    }
  }
</script>
