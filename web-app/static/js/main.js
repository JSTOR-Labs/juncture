window.isMobile = ('ontouchstart' in document.documentElement && /mobi/i.test(navigator.userAgent) )
window.isEditor = location.port === '5555' || location.hostname.indexOf('editor') == 0
console.log(`main.js: isMobile=${window.isMobile} height=${window.innerHeight}`)

/*
Array.from(document.querySelectorAll('p'))
  .forEach(el => {
    const observer = new IntersectionObserver ( 
      ([e]) => {
        console.log(e.boundingClientRect.top)
        console.log(e.intersectionRatio)
        if (e.isIntersecting) {
          console.log('VISIBLE')
          // e.target.classList.add('active')
          //return
        }
        if (e.boundingClientRect.top > 0) {
          console.log("BELOW")
        } else {
          console.log("ABOVE")
        }
        // e.target.classList.remove('active')
      },
      { root: null, threshold: [0,1], rootMargin: '800px' }
    )
    console.log(el)
    observer.observe(el)
  })
*/

// Use ScrollMagic to set paragraphs as 'active'
if (window.controller)  window.controller.destroy(true)
window.controller = new ScrollMagic.Controller({globalSceneOptions: {}})
window.triggerHook = window.isMobile ? 0.6 : (window.isEditor ? 300 : 200)/window.innerHeight
console.log(`triggerHook=${window.triggerHook}`)
Array.from(document.querySelectorAll('p')).forEach(p => {  // build scenes
  new ScrollMagic.Scene({
        triggerElement: p,
        triggerHook: window.triggerHook, 
        offset: -40,
        duration: p.clientHeight
    })
    .setClassToggle(p, 'active') // add class toggle
    // .addIndicators()
    .addTo(controller)
})

// Google Analytics
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-DRHNQSMN5Y');
