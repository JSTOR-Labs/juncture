<template>
    <div class="grid-container" :style="containerStyle">
        <div id="graphic-container" v-if="this.svg" :style="graphicStyle">
            <div id="graphic" v-html="this.svg"></div>
        </div>
        <div id="graphic-container" v-if="this.image" :style="graphicStyle">
            <img id="graphic" :src="this.image">
        </div>
        <div class="citation">
            <span class="title">{{this.items[0].title}}</span>
        </div>
    </div>
</template>

<script>
const viewerLabel = 'Graphic Viewer'
const viewerIcon = 'fas fa-atom'

module.exports = {
    name: 've-graphic',
    props: {
      items: Array,
      viewerIsActive: Boolean,
      width: Number,
      height: Number,
    },
    
    data: () => ({
        svg: undefined,
        image: undefined,
        viewerLabel,
        viewerIcon
    }),
    
    computed: {
        containerStyle() {
            return {
                // width: `${this.width}px`,
                height: this.viewerIsActive ? '100%' : '0',
                // maxHeight: `${this.height}px` ? `${this.height}px` : '',
                overflowY: 'auto !important',
            }
        },
        graphicItems() { return this.items.filter(item => item[this.componentName]) },
        input() { return this.graphicItems.length > 0 ? this.graphicItems[0].img || this.graphicItems[0].url || this.graphicItems[0].file : null },
        graphicStyle() {
            return {
                //width: `${this.width}px`,
                //height: `${this.height}px`,
                overflowY: 'auto !important',
                marginLeft: '0',   
            }
        }      
    },
    mounted() { this.loadDependencies(this.dependencies, 0, this.init) },
    methods: {
        init() {
            //check if svg
            if (this.input.split('.').pop() == 'svg'){
                fetch(this.input).then((resp) => resp.text())
                    .then((dataString) => {
                        this.svg = dataString;
                    })
            }
            else {
                this.image = this.input
            }
           
        },
    },
    watch: {
        items() {
            this.init()
        }
    }
  }
</script>

<style scoped>

    .grid-container {
        display: grid;
        grid-template-rows: auto 5%;
        grid-template-areas:
        "main"
        "footer";
        justify-items: center;
        align-items: start;
    }

    #graphic-container {
        grid-area: main;
        width:100%;
    }

    #graphic {
        width:100%;
    }

    .citation {
        /*
      grid-area: footer;
      z-index: 2;
      justify-self: stretch;
      align-self: stretch;
      background-color: #ccc;
      padding: 3px 6px;
        text-align: center;
        line-height: 1;
        */

        justify-self: stretch;
        /*align-self: stretch;*/
        max-height: 30px;
        overflow: auto; 
        background-color: #ccc;
        padding: 9px 6px;
        text-align: center;
        line-height: 1; 
    }

    .title {
      font-size: 0.9rem;
      font-weight: bold;
    }
</style>
